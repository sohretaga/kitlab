from django.urls import path
from .consumers import MessageConsumer, NotificationConsumer

websocket_urlpatterns = [
    path("ws/message/<int:conversation_id>/", MessageConsumer.as_asgi()),
    path("ws/notification/<int:user_id>/", NotificationConsumer.as_asgi()),
]