import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            self.room_group_name = f'notify_{user.id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        message = event.get('message', '')
        count = event.get('count', 0)
        action = event.get('action', 'STANDARD')
        caller = event.get('caller_name', '')
        room_url = event.get('room_url', '')

        await self.send(text_data=json.dumps({
            'message': message,
            'count': count,
            'action': action,
            'caller_name': caller,
            'room_url': room_url
        }))
