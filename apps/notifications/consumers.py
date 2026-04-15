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

    async def receive(self, text_data):
        """Handle messages FROM the client (e.g. decline/accept call)."""
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'CALL_DECLINED':
            # Notify the caller that the call was declined
            caller_id = data.get('caller_id')
            if caller_id:
                await self.channel_layer.group_send(
                    f'notify_{caller_id}',
                    {
                        'type': 'send_notification',
                        'message': 'Call was declined',
                        'count': 0,
                        'action': 'CALL_DECLINED',
                        'caller_name': '',
                        'room_url': ''
                    }
                )

    async def send_notification(self, event):
        message = event.get('message', '')
        count = event.get('count', 0)
        action = event.get('action', 'STANDARD')
        caller = event.get('caller_name', '')
        room_url = event.get('room_url', '')
        caller_id = event.get('caller_id', '')

        await self.send(text_data=json.dumps({
            'message': message,
            'count': count,
            'action': action,
            'caller_name': caller,
            'room_url': room_url,
            'caller_id': caller_id
        }))
