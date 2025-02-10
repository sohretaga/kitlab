from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, Conversation
from users.models import Profile
from django.contrib.auth.models import User
from dotenv import load_dotenv
from datetime import datetime
from django.conf import settings

import os
import pytz

load_dotenv()
azerbaijan_tz = pytz.timezone("Asia/Baku")

@receiver(post_save, sender=Message)
def send_new_message_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        target_user = instance.conversation.participants.exclude(id=instance.sender_id).first()
        room_group_name = f"notification_{target_user.id}"

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "new_message",
                "message": instance.content,
                "message_id": instance.id,
                "conversation_id": instance.conversation_id,
                'sender': instance.sender.username
            }
        )

@receiver(post_save, sender=Profile)
def send_welcome_message(sender, instance, created, **kwargs):
    welcome_message = settings.WELCOME_MESSAGE % instance.user.first_name

    messenger_username = os.getenv('MESSENGER_USERNAME')
    messenger_user = User.objects.filter(username=messenger_username).exists()

    if created and messenger_user and welcome_message:
        messenger_user = User.objects.get(username=messenger_username)
        target_user = instance.user
        conversation = Conversation.objects.create()
        conversation.participants.add(messenger_user, target_user)

        Message.objects.create(
            conversation=conversation,
            sender=messenger_user,
            content= welcome_message,
            timestamp=datetime.now(azerbaijan_tz)
        )