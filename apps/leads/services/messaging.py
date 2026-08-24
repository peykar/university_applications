from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.core.audit import get_system_user

from ..models import (
    Lead,
    LeadConversation,
    LeadMessage,
    LeadMessageSenderType,
)

User = get_user_model()


def ensure_conversation(lead: Lead) -> LeadConversation:
    conversation, _ = LeadConversation.objects.get_or_create(
        lead=lead,
        defaults={
            "created_by": lead.created_by,
            "updated_by": lead.updated_by,
        },
    )
    return conversation


def send_system_message(
    lead: Lead,
    body: str,
    *,
    performed_by=None,
) -> LeadMessage:
    actor = performed_by or get_system_user()
    conversation = ensure_conversation(lead)
    return LeadMessage.objects.create(
        conversation=conversation,
        sender=actor,
        sender_type=LeadMessageSenderType.SYSTEM,
        body=body,
        created_by=actor,
        updated_by=actor,
    )
