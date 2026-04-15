import json
from channels.generic.websocket import AsyncWebsocketConsumer

# In-memory room member tracking: room_group_name -> list of channel_names
# First channel in list is always the "initiator" (they send the offer)
room_members = {}


class VideoCallConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        members = room_members.setdefault(self.room_group_name, [])

        if len(members) == 0:
            # First peer — becomes the initiator (waits for second to join)
            members.append(self.channel_name)
            await self.send(text_data=json.dumps({
                'action': 'waiting_for_peer'
            }))
        elif len(members) == 1:
            # Second peer joined — tell the FIRST peer to create and send the offer
            members.append(self.channel_name)
            initiator_channel = members[0]
            await self.channel_layer.send(initiator_channel, {
                'type': 'make_offer'
            })
            # Also tell second peer they are ready to receive
            await self.send(text_data=json.dumps({
                'action': 'peer_joined',
                'peer_count': 2
            }))
        else:
            # Room is full (>2 peers) — reject
            await self.send(text_data=json.dumps({'action': 'room_full'}))
            await self.close()
            return

    async def disconnect(self, close_code):
        members = room_members.get(self.room_group_name, [])
        if self.channel_name in members:
            members.remove(self.channel_name)
        if not members:
            room_members.pop(self.room_group_name, None)

        # Notify the remaining peer
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'peer_event',
                'action': 'peer_left',
                'sender_channel': self.channel_name
            }
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action in ('new-offer', 'new-answer', 'new-ice-candidate'):
            # Relay signal to all OTHER peers (not back to sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_sdp',
                    'receive_dict': data,
                    'sender_channel': self.channel_name
                }
            )

    # ── Handlers ──────────────────────────────────────────────────────

    async def send_sdp(self, event):
        """Relay WebRTC signaling — never echo back to sender."""
        if event.get('sender_channel') == self.channel_name:
            return
        await self.send(text_data=json.dumps(event['receive_dict']))

    async def make_offer(self, event):
        """Tell the initiating peer to create and send the WebRTC offer."""
        await self.send(text_data=json.dumps({'action': 'make_offer'}))

    async def peer_event(self, event):
        """Broadcast peer join/leave events (filtered so sender doesn't get own event)."""
        if event.get('sender_channel') == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            'action': event['action']
        }))
