from django.contrib import admin

from .models import Conversation, ConversationParticipantState, Message, MessageAttachment

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(MessageAttachment)
admin.site.register(ConversationParticipantState)
