from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from message.models import Conversation
from django.db.models import Subquery, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from message.models import Conversation, Message
import json

class MessageView(LoginRequiredMixin, TemplateView):
    template_name = 'message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username=self.kwargs.get('username')

        if username and self.request.user.username != username:
            context['partner_user'] = username
            partner_user = get_object_or_404(User, username=self.kwargs.get('username'))
            conversation = Conversation.objects.filter(participants=self.request.user).filter(participants=partner_user).first()

            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(self.request.user, partner_user)


        conversations = Conversation.objects.filter(participants=self.request.user)

        partners = User.objects.filter(
            conversations__in=conversations
        ).exclude(
            id=self.request.user.id
        ).annotate(
            conversation_id=Subquery(
                conversations.filter(
                    participants=OuterRef('id')
                ).values('id')[:1]
            ),
            last_message=Subquery(
                Message.objects.filter(
                    conversation_id=OuterRef('conversation_id')
                )
                .order_by('-timestamp')
                .values('content')[:1]
            )
        )
        context['partners'] = partners
        return context

class LoadMessagesView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        conversation_id = data.get("conversation_id")

        if not conversation_id:
            return JsonResponse({"error": "conversation_id is required"}, status=400)
        
        messages = Conversation.objects.get(id=conversation_id).messages.values(
            'sender_id', 'content', 'timestamp', 'is_read'
        )

        return JsonResponse({
            'messages': list(messages),
            'full_name': self.request.user.first_name
        })