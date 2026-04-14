import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from apps.accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We will use room_name as a sorted combination of two user IDs: "chat_user1_user2"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
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
        action = data.get('action', 'text')
        sender_id = data['sender_id']
        
        if action == 'text':
            message_content = data['message']
            receiver_id = data['receiver_id']
            await self.save_message(sender_id, receiver_id, message_content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'text',
                    'message': message_content,
                    'sender_id': sender_id
                }
            )
        elif action == 'read_receipt':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'read_receipt',
                    'reader_id': sender_id
                }
            )
        elif action == 'edit_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'edit_message',
                    'msg_id': data.get('msg_id'),
                    'new_text': data.get('new_text'),
                    'sender_id': sender_id
                }
            )
        elif action == 'delete_message':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete_message',
                    'msg_id': data.get('msg_id'),
                    'sender_id': sender_id
                }
            )
        elif action == 'media':
            # View already saved the message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'media',
                    'attachment_url': data.get('attachment_url'),
                    'audio_url': data.get('audio_url'),
                    'sender_id': sender_id
                }
            )
        
    async def chat_message(self, event):
        payload = event.copy()
        del payload['type']
        await self.send(text_data=json.dumps(payload))
        
    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=sender, receiver=receiver, content=content)
        
        # Send Notification
        from apps.notifications.models import Notification
        notif = Notification.objects.create(
            user=receiver,
            message=f"New message from {sender.get_full_name() or sender.username}",
            notification_type=Notification.NotificationType.MESSAGE,
            action_link=f"/chat/room/{sender.id}/"
        )
        
        try:
            from channels.layers import get_channel_layer
            from asgireg.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notify_{receiver.id}',
                {
                    'type': 'send_notification',
                    'message': notif.message,
                    'count': receiver.notifications.filter(is_read=False).count(),
                    'action': 'STANDARD'
                }
            )
        except Exception:
            pass
