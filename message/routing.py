from django.urls import path
from .consumers import MessageConsumer

websocket_urlpatterns = [
    path("ws/message/<int:conversation_id>/", MessageConsumer.as_asgi()),
]