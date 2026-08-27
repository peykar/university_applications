from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.agents.models import Agent
from apps.core.models import BaseModel


class MessageSenderRole(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    AGENT = "agent", _("Agent")
    SYSTEM = "system", _("System")


class ConversationParticipantRole(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    AGENT = "agent", _("Agent")


class Conversation(BaseModel):
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_conversations",
    )
    subject_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subject_conversations",
    )
    subject_object_id = models.UUIDField(null=True, blank=True)
    subject = GenericForeignKey("subject_content_type", "subject_object_id")
    is_closed = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "agent",
                    "customer",
                    "subject_content_type",
                    "subject_object_id",
                ),
                name="unique_subject_conversation",
            ),
            models.UniqueConstraint(
                fields=("agent", "customer"),
                condition=models.Q(
                    subject_content_type__isnull=True,
                    subject_object_id__isnull=True,
                ),
                name="unique_general_conversation",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        subject_content_type__isnull=True,
                        subject_object_id__isnull=True,
                    )
                    | models.Q(
                        subject_content_type__isnull=False,
                        subject_object_id__isnull=False,
                    )
                ),
                name="conversation_subject_pair_consistent",
            ),
        )
        ordering = ("-updated_at",)

    @property
    def subject_kind(self) -> str:
        content_type = self.subject_content_type
        if content_type is None:
            return "general"
        return content_type.model

    @property
    def subject_label(self) -> str:
        subject = self.subject
        if subject is None:
            return str(_("General"))
        labels = {
            "lead": _("Applicant"),
            "student": _("Student"),
            "application": _("Application"),
        }
        prefix = labels.get(self.subject_kind, self.subject_kind.title())
        return f"{prefix} · {subject}"

    def get_agent_url(self) -> str:
        if self.subject_object_id is None:
            return reverse("agent-message-inbox")
        names = {
            "lead": "agent-applicant-detail",
            "student": "agent-student-detail",
            "application": "agent-application-detail",
        }
        name = names.get(self.subject_kind)
        if name is None:
            return reverse("agent-message-inbox")
        kwarg = {
            "lead": "lead_id",
            "student": "student_id",
            "application": "application_id",
        }[self.subject_kind]
        return reverse(name, kwargs={kwarg: self.subject_object_id}) + "#messages"

    def get_customer_url(self) -> str:
        if self.subject_kind == "lead" and self.subject_object_id:
            return reverse("lead-detail", kwargs={"lead_id": self.subject_object_id}) + "#messages"
        return reverse(
            "customer-conversation-detail",
            kwargs={"conversation_id": self.pk},
        )

    def __str__(self):
        return f"{self.agent} / {self.customer} / {self.subject_label}"


class Message(BaseModel):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages_sent",
    )
    sender_role = models.CharField(max_length=16, choices=MessageSenderRole.choices)
    body = models.TextField(blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = (
            models.Index(
                fields=("conversation", "sender_role", "created_at"),
                name="msg_conv_role_created_idx",
            ),
        )

    def clean(self):
        super().clean()
        if self.sender_role != MessageSenderRole.SYSTEM and not self.sender_id:
            raise ValidationError({"sender": _("Customer/agent messages require a sender.")})

    def __str__(self):
        return f"{self.conversation.subject_label} - {self.get_sender_role_display()}"


def message_attachment_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()[:16]
    return f"messages/{instance.message.conversation_id}/{uuid4().hex}{suffix}"


class MessageAttachment(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=message_attachment_upload_path, max_length=500)
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_name:
                self.original_name = Path(self.file.name).name
            if self.size is None:
                with suppress(OSError, ValueError):
                    self.size = self.file.size
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or Path(self.file.name).name


class ConversationParticipantState(BaseModel):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="participant_states",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_states",
    )
    participant_role = models.CharField(
        max_length=16,
        choices=ConversationParticipantRole.choices,
    )
    last_read_message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_read_by_states",
    )
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("conversation", "user", "participant_role"),
                name="unique_conversation_participant_state",
            ),
        )

    def clean(self):
        super().clean()
        last_read_message = self.last_read_message
        if (
            last_read_message is not None
            and last_read_message.conversation_id != self.conversation_id
        ):
            raise ValidationError(
                {"last_read_message": _("Last-read message must belong to this conversation.")}
            )

    def __str__(self):
        return f"{self.user} / {self.conversation_id} / {self.participant_role}"
