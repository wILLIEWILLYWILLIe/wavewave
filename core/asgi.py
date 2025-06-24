"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
application = get_asgi_application()

from home import routings

application = ProtocolTypeRouter({
	"http": application, 
    "websocket": AuthMiddlewareStack(URLRouter(routings.websocket_urlpatterns)), 
})