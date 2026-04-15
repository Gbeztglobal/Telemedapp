import os

# MUST set DJANGO_SETTINGS_MODULE before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.asgi import get_asgi_application

# Initialize Django BEFORE importing routing (which imports models)
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
