import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, Conversation
from django.utils.timezone import now
from channels.db import database_sync_to_async

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.room_name}"

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
        message_type = data['type']
        sender_id = data['sender']

        if message_type == 'chat_message':
            message_content = data['message']

            sender = await self.get_user(sender_id)
            conversation = await self.get_conversation(self.room_name)

            if sender and conversation:
                message = await self.create_message(conversation, sender, message_content)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message.content,
                        "sender_id": sender_id,
                        "full_name": sender.first_name,
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

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def create_message(self, conversation, sender, message_content):
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=message_content,
            timestamp=now()
        )