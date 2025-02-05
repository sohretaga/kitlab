import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, Conversation
from django.utils.timezone import now
from channels.db import database_sync_to_async
from core.redis_client import redis_client

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.add_user_to_presence()

    async def disconnect(self, close_code):
        await self.remove_user_from_presence()
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        sender_id = data['sender']

        if message_type == 'chat_message':
            message_content = data['message']
            timestamp = data['timestamp']

            sender = await self.get_user(sender_id)
            conversation = await self.get_conversation(self.room_name)

            if sender and conversation:
                is_read = False
                receiver = await self.get_receiver_user(sender_id, self.room_name)
                if receiver: is_read = await self.check_user_presence(receiver.id)

                message = await self.create_message(
                    conversation=conversation,
                    sender=sender,
                    message_content=message_content,
                    timestamp=timestamp,
                    is_read=is_read
                )

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message.content,
                        "sender_id": sender_id,
                        "full_name": sender.first_name,
                        "is_read": message.is_read,
                        "timestamp": str(message.timestamp)
                    }
                )
        elif message_type == 'chat_typing':
            has_message = data['has_message']

            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_typing",
                        "has_message": has_message,
                        "sender_id": sender_id
                    }
                )
        elif message_type == 'member_joined':
            await self.make_messages_as_read(self.room_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "member_joined",
                    "all_read": True,
                    "sender_id": sender_id
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def member_joined(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def add_user_to_presence(self):
        cache_key = f"chat_presence:{self.room_group_name}"
        user_id = str(self.user.id)
        redis_client.sadd(cache_key, user_id)
        redis_client.expire(cache_key, 86400)  # 24 hour TTL

    @database_sync_to_async
    def remove_user_from_presence(self):
        cache_key = f"chat_presence:{self.room_group_name}"
        user_id = str(self.user.id)
        redis_client.srem(cache_key, user_id)

    @database_sync_to_async
    def check_user_presence(self, user_id):
        cache_key = f"chat_presence:{self.room_group_name}"
        return redis_client.sismember(cache_key, str(user_id))
    
    @database_sync_to_async
    def get_receiver_user(self, sender_id, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        return conversation.participants.exclude(id=sender_id).first()

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def make_messages_as_read(self, conversation_id):
        Conversation.objects.get(id=conversation_id).messages.exclude(
            sender=self.user
        ).update(is_read=True)

    @database_sync_to_async
    def create_message(self, conversation, sender, message_content, timestamp, is_read):
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=message_content,
            is_read=is_read,
            timestamp=timestamp
        )