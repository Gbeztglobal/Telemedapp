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

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'new-offer' or action == 'new-answer' or action == 'new-ice-candidate':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_sdp',
                    'receive_dict': data
                }
            )
            
    async def send_sdp(self, event):
        receive_dict = event['receive_dict']
        await self.send(text_data=json.dumps(receive_dict))
