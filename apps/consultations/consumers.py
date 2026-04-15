import json
from channels.generic.websocket import AsyncWebsocketConsumer

# In-memory room state.
# Structure: room_group_name -> {
#     'members':   [channel_name, ...],   # index=0 → initiator
#     'usernames': [username, ...]         # parallel list for reconnect handling
# }
room_state = {}


class VideoCallConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name       = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'

        user = self.scope.get('user')
        self.username = (
            user.username
            if user and user.is_authenticated
            else self.channel_name          # fallback for anonymous
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        state     = room_state.setdefault(self.room_group_name, {'members': [], 'usernames': []})
        members   = state['members']
        usernames = state['usernames']

        # ── Reconnect: same user replacing their old slot ──────────────
        if self.username in usernames:
            idx = usernames.index(self.username)
            old_channel = members[idx]
            members[idx]   = self.channel_name
            usernames[idx] = self.username
            # Discard the stale channel from the group (best-effort)
            try:
                await self.channel_layer.group_discard(self.room_group_name, old_channel)
            except Exception:
                pass

            if len(members) == 2:
                # Room is full again → initiator re-sends the offer
                await self.channel_layer.send(members[0], {'type': 'make_offer'})
                await self.send(text_data=json.dumps({
                    'action': 'peer_joined',
                    'peer_count': 2,
                }))
            else:
                await self.send(text_data=json.dumps({'action': 'waiting_for_peer'}))
            return

        # ── Fresh join ────────────────────────────────────────────────
        if len(members) == 0:
            members.append(self.channel_name)
            usernames.append(self.username)
            await self.send(text_data=json.dumps({'action': 'waiting_for_peer'}))

        elif len(members) == 1:
            members.append(self.channel_name)
            usernames.append(self.username)
            # Tell the initiator (slot 0) to create and send the WebRTC offer
            await self.channel_layer.send(members[0], {'type': 'make_offer'})
            await self.send(text_data=json.dumps({
                'action': 'peer_joined',
                'peer_count': 2,
            }))

        else:
            # Room is full (> 2 unique peers)
            await self.send(text_data=json.dumps({'action': 'room_full'}))
            await self.close()

    # ──────────────────────────────────────────────────────────────────
    async def disconnect(self, close_code):
        state     = room_state.get(self.room_group_name, {'members': [], 'usernames': []})
        members   = state['members']
        usernames = state['usernames']

        if self.channel_name in members:
            idx = members.index(self.channel_name)
            members.pop(idx)
            usernames.pop(idx)

        if not members:
            room_state.pop(self.room_group_name, None)

        # Notify remaining peer
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'peer_event',
                'action': 'peer_left',
                'sender_channel': self.channel_name,
            }
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # ──────────────────────────────────────────────────────────────────
    async def receive(self, text_data):
        data   = json.loads(text_data)
        action = data.get('action')

        if action in ('new-offer', 'new-answer', 'new-ice-candidate'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_sdp',
                    'receive_dict': data,
                    'sender_channel': self.channel_name,
                }
            )

    # ── Channel-layer handlers ────────────────────────────────────────

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
        await self.send(text_data=json.dumps({'action': event['action']}))
