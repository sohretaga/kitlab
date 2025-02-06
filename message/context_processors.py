def new_messages(request):
    new_message_count = 0

    if request.user.is_authenticated:
        conversations = request.user.conversations.all()

        for conversation in conversations:
            messages = conversation.messages.exclude(sender=request.user).filter(is_read=False)
            new_message_count += messages.count()

    return {
        "new_message_count": new_message_count
    }