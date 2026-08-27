from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone

from apps.core.audit import get_system_user

from .models import (
    Conversation,
    ConversationParticipantRole,
    ConversationParticipantState,
    Message,
    MessageAttachment,
    MessageSenderRole,
)


def subject_agent(subject):
    if subject.__class__.__name__ == "Application":
        return subject.agent or subject.student.agent
    return getattr(subject, "agent", None)


def subject_customer(subject):
    if subject.__class__.__name__ == "Application":
        return subject.student.user
    return getattr(subject, "user", None)


def validate_conversation_subject(*, agent, customer, subject) -> None:
    if subject is None:
        return
    if subject_agent(subject) != agent:
        raise ValidationError("Conversation subject belongs to a different Agent.")
    if subject_customer(subject) != customer:
        raise ValidationError("Conversation subject belongs to a different customer.")


def get_or_create_conversation(*, subject=None, agent=None, customer=None) -> Conversation:
    if subject is not None:
        agent = agent or subject_agent(subject)
        customer = customer or subject_customer(subject)
    if agent is None or customer is None:
        raise ValidationError("Conversation requires an Agent and customer.")
    validate_conversation_subject(agent=agent, customer=customer, subject=subject)
    content_type = ContentType.objects.get_for_model(subject) if subject is not None else None
    object_id = subject.pk if subject is not None else None
    conversation, _ = Conversation.objects.get_or_create(
        agent=agent,
        customer=customer,
        subject_content_type=content_type,
        subject_object_id=object_id,
        defaults={"created_by": customer, "updated_by": customer},
    )
    return conversation


def can_access_as_agent(user, conversation: Conversation) -> bool:
    return bool(
        user.is_authenticated
        and (user.is_superuser or conversation.agent.users.filter(pk=user.pk).exists())
    )


def can_access_as_customer(user, conversation: Conversation) -> bool:
    return bool(user.is_authenticated and conversation.customer_id == user.pk)


def send_message(*, conversation, sender, sender_role, body="", attachment=None) -> Message:
    if conversation.is_closed:
        raise ValidationError("This conversation is closed.")
    if sender_role == MessageSenderRole.CUSTOMER:
        if not can_access_as_customer(sender, conversation):
            raise PermissionDenied("You cannot send messages in this conversation.")
    elif sender_role == MessageSenderRole.AGENT and not can_access_as_agent(sender, conversation):
        raise PermissionDenied("You cannot send messages for this Agent.")
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        sender_role=sender_role,
        body=body,
        created_by=sender,
        updated_by=sender,
    )
    if attachment:
        MessageAttachment.objects.create(
            message=message,
            file=attachment,
            original_name=attachment.name,
            content_type=getattr(attachment, "content_type", ""),
            size=getattr(attachment, "size", None),
            created_by=sender,
            updated_by=sender,
        )
    conversation.updated_by = sender
    conversation.save(update_fields=("updated_by", "updated_at"))
    return message


def send_system_message(subject, body: str, *, performed_by=None) -> Message:
    actor = performed_by or get_system_user()
    conversation = get_or_create_conversation(subject=subject)
    return Message.objects.create(
        conversation=conversation,
        sender=actor,
        sender_role=MessageSenderRole.SYSTEM,
        body=body,
        created_by=actor,
        updated_by=actor,
    )


def mark_conversation_read(*, conversation, user, participant_role) -> None:
    if participant_role == ConversationParticipantRole.AGENT:
        if not can_access_as_agent(user, conversation):
            raise PermissionDenied
        incoming = conversation.messages.filter(sender_role=MessageSenderRole.CUSTOMER)
    else:
        if not can_access_as_customer(user, conversation):
            raise PermissionDenied
        incoming = conversation.messages.filter(
            sender_role__in=(MessageSenderRole.AGENT, MessageSenderRole.SYSTEM)
        )
    latest = incoming.order_by("-created_at").first()
    state, _ = ConversationParticipantState.objects.get_or_create(
        conversation=conversation,
        user=user,
        participant_role=participant_role,
        defaults={"created_by": user, "updated_by": user},
    )
    state.last_read_message = latest
    state.last_read_at = timezone.now()
    state.updated_by = user
    state.save(update_fields=("last_read_message", "last_read_at", "updated_by", "updated_at"))


def _unread_messages(*, user, participant_role):
    state = ConversationParticipantState.objects.filter(
        conversation_id=OuterRef("conversation_id"),
        user=user,
        participant_role=participant_role,
    )
    if participant_role == ConversationParticipantRole.AGENT:
        incoming = Message.objects.filter(sender_role=MessageSenderRole.CUSTOMER)
    else:
        incoming = Message.objects.filter(
            sender_role__in=(MessageSenderRole.AGENT, MessageSenderRole.SYSTEM)
        )
    return incoming.annotate(
        participant_last_read_at=Subquery(state.values("last_read_at")[:1])
    ).filter(
        Q(participant_last_read_at__isnull=True)
        | Q(created_at__gt=Subquery(state.values("last_read_at")[:1]))
    )


def unread_count_for_conversation(*, conversation, user, participant_role) -> int:
    return (
        _unread_messages(
            user=user,
            participant_role=participant_role,
        )
        .filter(conversation=conversation)
        .count()
    )


def agent_unread_count(user, *, agent=None) -> int:
    if not user.is_authenticated:
        return 0
    messages = _unread_messages(
        user=user,
        participant_role=ConversationParticipantRole.AGENT,
    )
    if user.is_superuser:
        if agent is not None:
            messages = messages.filter(conversation__agent=agent)
        return messages.count()
    messages = messages.filter(conversation__agent__users=user)
    if agent is not None:
        messages = messages.filter(conversation__agent=agent)
    return messages.distinct().count()


def customer_unread_count(user) -> int:
    if not user.is_authenticated:
        return 0
    return (
        _unread_messages(
            user=user,
            participant_role=ConversationParticipantRole.CUSTOMER,
        )
        .filter(conversation__customer=user)
        .count()
    )
