from django.urls import path
from .views import MessageView, LoadMessagesView

urlpatterns = [
    path('message', MessageView.as_view(), name='message'),
    path('message/<str:username>', MessageView.as_view(), name='message-with-username'),

    # API's
    path('api/load-messages', LoadMessagesView.as_view())
]