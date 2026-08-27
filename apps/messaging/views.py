from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MessageForm
from .models import (
    Conversation,
    ConversationParticipantRole,
    MessageSenderRole,
)
from .services import (
    mark_conversation_read,
    send_message,
    unread_count_for_conversation,
)


@login_required
def customer_message_inbox(request):
    conversations = request.user.customer_conversations.select_related(
        "agent", "subject_content_type"
    ).order_by("-updated_at")
    rows = []
    for conversation in conversations:
        rows.append(
            {
                "conversation": conversation,
                "unread_count": unread_count_for_conversation(
                    conversation=conversation,
                    user=request.user,
                    participant_role=ConversationParticipantRole.CUSTOMER,
                ),
            }
        )
    return render(request, "messaging/customer_inbox.html", {"conversation_rows": rows})


@login_required
def customer_conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.select_related("agent", "subject_content_type"),
        pk=conversation_id,
        customer=request.user,
    )
    conversation_messages = conversation.messages.select_related("sender").prefetch_related(
        "attachments"
    )
    mark_conversation_read(
        conversation=conversation,
        user=request.user,
        participant_role=ConversationParticipantRole.CUSTOMER,
    )
    return render(
        request,
        "messaging/customer_conversation.html",
        {
            "conversation": conversation,
            "conversation_messages": conversation_messages,
            "message_form": MessageForm(),
        },
    )


@login_required
@require_POST
def customer_conversation_send(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        customer=request.user,
    )
    form = MessageForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Write a message or attach a file.")
        return redirect("customer-conversation-detail", conversation_id=conversation.pk)
    send_message(
        conversation=conversation,
        sender=request.user,
        sender_role=MessageSenderRole.CUSTOMER,
        body=form.cleaned_data.get("body", ""),
        attachment=form.cleaned_data.get("attachment"),
    )
    return redirect("customer-conversation-detail", conversation_id=conversation.pk)
