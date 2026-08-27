from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.leads.models import (
    Lead,
    LeadConversation,
    LeadMessage,
    LeadMessageAttachment,
    LeadMessageRead,
)
from apps.messaging.models import (
    Conversation,
    ConversationParticipantRole,
    ConversationParticipantState,
    Message,
    MessageAttachment,
    MessageSenderRole,
)


class Command(BaseCommand):
    help = (
        "Idempotently migrate legacy Lead messaging data into the generic "
        "Conversation/Message messaging system."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and report what would be migrated without committing changes.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        lead_content_type = ContentType.objects.get_for_model(
            Lead,
            for_concrete_model=False,
        )

        counters: defaultdict[str, int] = defaultdict(int)
        skipped_conversations: list[str] = []
        conversation_map: dict[Any, Any] = {}

        legacy_conversations = LeadConversation.objects.select_related("lead").all()
        for legacy_conversation in legacy_conversations.iterator():
            lead = legacy_conversation.lead
            if not lead.agent_id or not lead.user_id:
                counters["conversations_skipped"] += 1
                skipped_conversations.append(str(legacy_conversation.pk))
                continue

            conversation, created = Conversation.objects.get_or_create(
                agent_id=lead.agent_id,
                customer_id=lead.user_id,
                subject_content_type=lead_content_type,
                subject_object_id=lead.pk,
                defaults={
                    "is_closed": legacy_conversation.is_closed,
                    "created_by_id": legacy_conversation.created_by_id,
                    "updated_by_id": legacy_conversation.updated_by_id,
                },
            )
            conversation_map[legacy_conversation.pk] = conversation.pk
            counters["conversations_created" if created else "conversations_existing"] += 1

        sender_roles = {
            "customer": MessageSenderRole.CUSTOMER,
            "staff": MessageSenderRole.AGENT,
            "system": MessageSenderRole.SYSTEM,
        }

        legacy_messages = LeadMessage.objects.select_related("conversation").all()
        for legacy_message in legacy_messages.iterator():
            conversation_id = conversation_map.get(legacy_message.conversation_id)
            if conversation_id is None:
                counters["messages_skipped"] += 1
                continue

            message, created = Message.objects.get_or_create(
                pk=legacy_message.pk,
                defaults={
                    "conversation_id": conversation_id,
                    "sender_id": legacy_message.sender_id,
                    "sender_role": sender_roles.get(
                        legacy_message.sender_type,
                        MessageSenderRole.SYSTEM,
                    ),
                    "body": legacy_message.body,
                    "edited_at": legacy_message.edited_at,
                    "created_by_id": legacy_message.created_by_id,
                    "updated_by_id": legacy_message.updated_by_id,
                },
            )
            if not created and message.conversation_id != conversation_id:
                raise CommandError(
                    f"Generic Message {message.pk} already exists in another conversation."
                )
            counters["messages_created" if created else "messages_existing"] += 1

        legacy_attachments = LeadMessageAttachment.objects.all()
        for legacy_attachment in legacy_attachments.iterator():
            if not Message.objects.filter(pk=legacy_attachment.message_id).exists():
                counters["attachments_skipped"] += 1
                continue

            attachment, created = MessageAttachment.objects.get_or_create(
                pk=legacy_attachment.pk,
                defaults={
                    "message_id": legacy_attachment.message_id,
                    "file": legacy_attachment.file,
                    "original_name": legacy_attachment.original_name,
                    "content_type": legacy_attachment.content_type,
                    "size": legacy_attachment.size,
                    "created_by_id": legacy_attachment.created_by_id,
                    "updated_by_id": legacy_attachment.updated_by_id,
                },
            )
            if not created and attachment.message_id != legacy_attachment.message_id:
                raise CommandError(
                    f"Generic attachment {attachment.pk} belongs to another message."
                )
            counters["attachments_created" if created else "attachments_existing"] += 1

        # Collapse old per-message receipts to the furthest read message per
        # conversation/user. This preserves unread semantics for the cursor model.
        latest_receipts: dict[tuple[Any, Any], LeadMessageRead] = {}
        receipts = LeadMessageRead.objects.select_related("message").order_by(
            "message__created_at",
            "read_at",
        )
        for receipt in receipts.iterator():
            conversation_id = conversation_map.get(receipt.message.conversation_id)
            if conversation_id is None:
                counters["read_receipts_skipped"] += 1
                continue
            latest_receipts[(conversation_id, receipt.user_id)] = receipt

        for (conversation_id, user_id), receipt in latest_receipts.items():
            conversation = Conversation.objects.get(pk=conversation_id)
            role = (
                ConversationParticipantRole.CUSTOMER
                if conversation.customer_id == user_id
                else ConversationParticipantRole.AGENT
            )
            _, created = ConversationParticipantState.objects.update_or_create(
                conversation_id=conversation_id,
                user_id=user_id,
                participant_role=role,
                defaults={
                    "last_read_message_id": receipt.message_id,
                    "last_read_at": receipt.read_at,
                    "created_by_id": user_id,
                    "updated_by_id": user_id,
                },
            )
            counters["states_created" if created else "states_updated"] += 1

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Legacy messaging migration"))
        self.stdout.write(
            f"Conversations: {counters['conversations_created']} created, "
            f"{counters['conversations_existing']} already present, "
            f"{counters['conversations_skipped']} skipped"
        )
        self.stdout.write(
            f"Messages: {counters['messages_created']} created, "
            f"{counters['messages_existing']} already present, "
            f"{counters['messages_skipped']} skipped"
        )
        self.stdout.write(
            f"Attachments: {counters['attachments_created']} created, "
            f"{counters['attachments_existing']} already present, "
            f"{counters['attachments_skipped']} skipped"
        )
        self.stdout.write(
            f"Read states: {counters['states_created']} created, "
            f"{counters['states_updated']} updated, "
            f"{counters['read_receipts_skipped']} receipts skipped"
        )

        if skipped_conversations:
            self.stdout.write(
                self.style.WARNING(
                    "Skipped legacy conversations without both an Agent and customer: "
                    + ", ".join(skipped_conversations)
                )
            )

        if dry_run:
            transaction.set_rollback(True)
            self.stdout.write(self.style.WARNING("Dry run: all changes rolled back."))
        else:
            self.stdout.write(
                self.style.SUCCESS("Legacy messages are available in the generic messaging system.")
            )
