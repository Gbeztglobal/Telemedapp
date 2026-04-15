import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify others that a peer joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'send_sdp', 'receive_dict': {'action': 'peer-joined'}}
        )

    async def disconnect(self, close_code):
        # Notify others that peer left (call ended)
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'send_sdp', 'receive_dict': {'action': 'call-ended'}}
        )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        RELAY_ACTIONS = {
            'new-offer', 'new-answer', 'new-ice-candidate',
            'call-ended', 'peer-joined'
        }

        if action in RELAY_ACTIONS:
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'send_sdp', 'receive_dict': data}
            )

    async def send_sdp(self, event):
        await self.send(text_data=json.dumps(event['receive_dict']))
