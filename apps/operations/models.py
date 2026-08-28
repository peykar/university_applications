from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.agents.models import Agent
from apps.core.models import BaseModel


class TodoStatus(models.TextChoices):
    CREATED = "created", _("Created")
    IN_PROGRESS = "in_progress", _("In progress")
    DONE = "done", _("Done")
    CANCELLED = "cancelled", _("Cancelled")


class Todo(BaseModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=TodoStatus.choices,
        default=TodoStatus.CREATED,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_agent_todos",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    subject_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subject_todos",
    )
    subject_object_id = models.UUIDField(null=True, blank=True)
    subject = GenericForeignKey("subject_content_type", "subject_object_id")

    class Meta:
        ordering = ("status", "due_date", "-created_at")
        constraints = (
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
                name="todo_subject_pair_consistent",
            ),
        )
        indexes = (
            models.Index(fields=("agent", "status", "due_date")),
            models.Index(fields=("subject_content_type", "subject_object_id")),
        )

    def clean(self):
        super().clean()
        if (
            self.assignee_id
            and self.agent_id
            and not self.agent.users.filter(pk=self.assignee_id).exists()
        ):
            raise ValidationError(
                {"assignee": _("Assignee must belong to the owning Agent organization.")}
            )

    def __str__(self):
        return self.title


class TodoComment(BaseModel):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )
    body = models.TextField()

    class Meta:
        ordering = ("created_at",)

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError(_("TODO comments are immutable after posting."))
        return super().save(*args, **kwargs)


class CommunicationChannel(models.TextChoices):
    PHONE = "phone", _("Phone")
    EMAIL = "email", _("Email")
    WHATSAPP = "whatsapp", _("WhatsApp")
    TELEGRAM = "telegram", _("Telegram")
    IN_PERSON = "in_person", _("In person")
    VIDEO_CALL = "video_call", _("Video call")
    OTHER = "other", _("Other")


class CommunicationCounterpartyType(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    UNIVERSITY = "university", _("University")
    OTHER = "other", _("Other")


class CommunicationLog(BaseModel):
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="communication_logs",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="performed_communication_logs",
    )
    occurred_at = models.DateTimeField()
    channel = models.CharField(max_length=20, choices=CommunicationChannel.choices)
    counterparty_type = models.CharField(
        max_length=20,
        choices=CommunicationCounterpartyType.choices,
    )
    counterparty_name = models.CharField(max_length=255, blank=True)
    summary = models.TextField()
    subject_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subject_communication_logs",
    )
    subject_object_id = models.UUIDField(null=True, blank=True)
    subject = GenericForeignKey("subject_content_type", "subject_object_id")

    class Meta:
        ordering = ("-occurred_at", "-created_at")
        constraints = (
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
                name="communication_subject_pair_consistent",
            ),
        )
        indexes = (
            models.Index(fields=("agent", "occurred_at")),
            models.Index(fields=("subject_content_type", "subject_object_id")),
        )

    def __str__(self):
        return f"{self.get_channel_display()} · {self.occurred_at:%Y-%m-%d}"


class CommunicationLogRevision(BaseModel):
    communication = models.ForeignKey(
        CommunicationLog,
        on_delete=models.CASCADE,
        related_name="revisions",
    )
    revised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )
    snapshot = models.JSONField(default=dict)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError(_("Communication revisions are immutable."))
        return super().save(*args, **kwargs)
