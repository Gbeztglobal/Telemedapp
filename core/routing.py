from django.urls import re_path
from apps.consultations import consumers as webrtc_consumers
from apps.messaging import consumers as chat_consumers
from apps.notifications import consumers as notify_consumers

websocket_urlpatterns = [
    re_path(r'ws/call/(?P<room_name>\w+)/$', webrtc_consumers.VideoCallConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', notify_consumers.NotificationConsumer.as_asgi()),
]
