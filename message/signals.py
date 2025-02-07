from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
