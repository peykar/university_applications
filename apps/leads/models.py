from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.agents.models import Agent
from apps.core.models import BaseModel
from apps.geography.models import City, Country
from apps.students.models import DocumentType, EnglishTestType, Gender
from apps.universities.models import (
    Currency,
    DegreeType,
    Department,
    Program,
    ProgramLanguage,
    ProgramOffering,
    University,
    UniversityType,
)


class LeadStatus(models.TextChoices):
    NEW = "new", _("New")
    ASSIGNED = "assigned", _("Assigned")
    FINALIZED = "finalized", _("Finalized")
    CLOSED = "closed", _("Closed")


class LeadSource(models.TextChoices):
    WEBSITE = "website", _("Website")
    AGENT = "agent", _("Agent")
    STAFF = "staff", _("Staff")
    SYSTEM = "system", _("System")
    OTHER = "other", _("Other")


class Lead(BaseModel):
    """
    Provisional applicant data.

    Lead data is intentionally less strict than Student data. It represents
    information supplied before staff/system validation and finalization.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="leads",
        help_text=_("Authenticated account that owns and manages this applicant."),
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=_("Internal staff user currently responsible for this lead."),
    )

    status = models.CharField(
        max_length=32,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
    )
    source = models.CharField(
        max_length=24,
        choices=LeadSource.choices,
        default=LeadSource.WEBSITE,
    )
    needs_program_recommendation = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_(
            "The applicant is unsure which programs are suitable and wants "
            "TurkDemy staff/system to investigate and suggest options."
        ),
    )

    first_name = models.CharField(max_length=150, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    country_of_birth = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="leads_born",
    )
    nationality = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="leads_nationality",
    )
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True)

    email = models.EmailField(blank=True)
    # Deliberately no strict phone validator here: Lead data is provisional.
    cell = models.CharField(max_length=40, blank=True)
    birthdate = models.DateField(null=True, blank=True)

    english_test_type = models.CharField(
        max_length=20,
        choices=EnglishTestType.choices,
        blank=True,
    )
    english_language_test_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    high_school_gpa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    high_school_gpa_scale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    father_name = models.CharField(max_length=255, blank=True)
    mother_name = models.CharField(max_length=255, blank=True)

    passport_no = models.CharField(max_length=100, blank=True, db_index=True)
    passport_issuing_authority = models.CharField(max_length=255, blank=True)
    passport_date_of_issue = models.DateField(null=True, blank=True)
    passport_date_of_expiry = models.DateField(null=True, blank=True)

    country_of_residence = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="leads_residing",
    )
    city_of_residence = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    educational_background = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text=_("Internal notes."))

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    converted_student = models.OneToOneField(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_lead",
    )
    converted_at = models.DateTimeField(null=True, blank=True)

    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    close_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=("user", "status")),
            models.Index(fields=("assigned_to", "status")),
            models.Index(fields=("needs_program_recommendation", "status")),
        )

    def save(self, *args, **kwargs):
        if self.status not in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
            self.status = LeadStatus.ASSIGNED if self.assigned_to_id else LeadStatus.NEW
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = tuple(set(update_fields) | {"status"})
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class LeadPreference(BaseModel):
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="preferences",
    )

    tuition_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    tuition_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    tuition_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        blank=True,
    )

    preferred_languages = models.ManyToManyField(
        ProgramLanguage,
        blank=True,
        related_name="lead_preferences",
    )
    preferred_cities = models.ManyToManyField(
        City,
        blank=True,
        related_name="lead_preferences",
    )
    preferred_universities = models.ManyToManyField(
        University,
        blank=True,
        related_name="lead_preferences",
    )
    preferred_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name="lead_preferences",
    )

    preferred_degrees = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Degree codes such as bachelor, master or phd."),
    )
    preferred_university_types = models.JSONField(
        default=list,
        blank=True,
        help_text=_("University type codes such as public or private."),
    )

    requires_dormitory = models.BooleanField(null=True, blank=True)
    requires_erasmus = models.BooleanField(null=True, blank=True)

    notes = models.TextField(
        blank=True,
        help_text=_("Additional study preferences or constraints."),
    )

    def clean(self):
        super().clean()

        if (
            self.tuition_min is not None
            and self.tuition_max is not None
            and self.tuition_min > self.tuition_max
        ):
            raise ValidationError(
                {"tuition_max": _("Maximum tuition must be greater than minimum tuition.")}
            )

        valid_degrees = {choice for choice, _ in DegreeType.choices}
        invalid_degrees = set(self.preferred_degrees or []) - valid_degrees
        if invalid_degrees:
            raise ValidationError(
                {"preferred_degrees": _("One or more degree values are invalid.")}
            )

        valid_types = {choice for choice, _ in UniversityType.choices}
        invalid_types = set(self.preferred_university_types or []) - valid_types
        if invalid_types:
            raise ValidationError(
                {"preferred_university_types": _("One or more university types are invalid.")}
            )

    def __str__(self):
        return f"Preferences for {self.lead}"


class LeadProgramInterestSource(models.TextChoices):
    USER = "user", _("User-added")
    AGENT = "agent", _("Agent-suggested")


class LeadProgramInterest(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="program_interests",
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="lead_interests",
    )
    program_offering = models.ForeignKey(
        ProgramOffering,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lead_interests",
        help_text=_(
            "Specific intake/offering when known. Program-level interest is "
            "allowed without selecting an offering."
        ),
    )

    source = models.CharField(
        max_length=16,
        choices=LeadProgramInterestSource.choices,
        default=LeadProgramInterestSource.USER,
    )

    suggested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    suggestion_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    converted_application = models.OneToOneField(
        "applications.Application",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_lead_interest",
    )

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("lead", "program"),
                condition=models.Q(program_offering__isnull=True),
                name="unique_lead_program_without_offering",
            ),
            models.UniqueConstraint(
                fields=("lead", "program", "program_offering"),
                condition=models.Q(program_offering__isnull=False),
                name="unique_lead_program_offering_interest",
            ),
        )

    def clean(self):
        super().clean()
        offering = self.program_offering if self.program_offering_id else None
        if offering is not None and offering.program_id != self.program_id:
            raise ValidationError(
                {"program_offering": _("Offering must belong to the selected program.")}
            )

    def __str__(self):
        return f"{self.lead} → {self.program}"


def lead_document_upload_path(instance, filename):
    return f"leads/{instance.lead_id}/documents/{filename}"


class LeadDocumentReviewStatus(models.TextChoices):
    PENDING = "pending", _("Needs review")
    APPROVED = "approved", _("Approved")
    REPLACEMENT_REQUESTED = "replacement_requested", _("Replacement requested")


class LeadDocument(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
    )
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=lead_document_upload_path)
    description = models.TextField(blank=True)

    review_status = models.CharField(
        max_length=32,
        choices=LeadDocumentReviewStatus.choices,
        default=LeadDocumentReviewStatus.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    source_message_attachment = models.OneToOneField(
        "LeadMessageAttachment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promoted_document",
        help_text=_("Chat attachment this document was promoted from, when applicable."),
    )

    # Kept for compatibility with existing conversion code. It is synchronized
    # with review_status by the agent review workflow.
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    converted_student_document = models.OneToOneField(
        "students.StudentDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_lead_document",
    )

    def save(self, *args, **kwargs):
        if self.file and not self.name:
            self.name = Path(self.file.name).name
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lead} - {self.get_document_type_display()}"


class LeadActivityType(models.TextChoices):
    CREATED = "created", _("Created")
    NOTE = "note", _("Note")
    APPLICANT_UPDATED = "applicant_updated", _("Applicant data updated")
    INTERNAL_NOTES_UPDATED = "internal_notes_updated", _("Internal notes updated")
    STATUS_CHANGED = "status_changed", _("Status changed")
    ASSIGNED = "assigned", _("Assigned")
    REASSIGNED = "reassigned", _("Reassigned")
    CLOSED = "closed", _("Closed")
    REOPENED = "reopened", _("Reopened")
    VALIDATED = "validated", _("Validated")
    DOCUMENT_UPLOADED = "document_uploaded", _("Document uploaded")
    DOCUMENT_REVIEWED = "document_reviewed", _("Document reviewed")
    PROGRAM_ADDED = "program_added", _("Program added")
    PROGRAM_SUGGESTED = "program_suggested", _("Program suggested")
    PROGRAM_RESPONSE = "program_response", _("Program response")
    RECOMMENDATIONS_GENERATED = "recommendations_generated", _("Recommendations generated")
    FINALIZED = "finalized", _("Finalized")


class LeadActivity(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    activity_type = models.CharField(
        max_length=40,
        choices=LeadActivityType.choices,
    )
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    is_customer_visible = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.lead}: {self.get_activity_type_display()}"


class LeadConversation(BaseModel):
    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE,
        related_name="conversation",
    )
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Conversation: {self.lead}"


class LeadMessageSenderType(models.TextChoices):
    CUSTOMER = "customer", _("Customer")
    STAFF = "staff", _("Staff")
    SYSTEM = "system", _("System")


class LeadMessage(BaseModel):
    conversation = models.ForeignKey(
        LeadConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    sender_type = models.CharField(
        max_length=16,
        choices=LeadMessageSenderType.choices,
    )
    body = models.TextField(blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)

    def clean(self):
        super().clean()
        if self.sender_type != LeadMessageSenderType.SYSTEM and not self.sender_id:
            raise ValidationError({"sender": _("Customer/staff messages require a sender.")})
        if not self.body and not self.pk:
            # An attachment can be added immediately after message creation;
            # public form still requires either body or attachment.
            pass

    def __str__(self):
        return f"{self.conversation.lead} - {self.get_sender_type_display()}"


def lead_document_version_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()[:16]
    stored_name = f"{uuid4().hex}{suffix}"
    return (
        f"leads/{instance.document.lead_id}/documents/history/{instance.document_id}/{stored_name}"
    )


class LeadDocumentVersion(BaseModel):
    """Archived copy of a LeadDocument before a customer replacement."""

    document = models.ForeignKey(
        LeadDocument,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    file = models.FileField(
        upload_to=lead_document_version_upload_path,
        max_length=500,
    )
    original_name = models.CharField(max_length=255, blank=True)
    review_status = models.CharField(
        max_length=32,
        choices=LeadDocumentReviewStatus.choices,
    )
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class LeadDocumentReviewHistory(BaseModel):
    """Audit trail for document review decisions."""

    document = models.ForeignKey(
        LeadDocument,
        on_delete=models.CASCADE,
        related_name="review_history",
    )
    review_status = models.CharField(
        max_length=32,
        choices=LeadDocumentReviewStatus.choices,
    )
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    reviewed_at = models.DateTimeField()

    class Meta:
        ordering = ("-reviewed_at", "-created_at")


def lead_message_attachment_upload_path(instance, filename):
    """Build a bounded storage path while preserving the original extension."""
    suffix = Path(filename).suffix.lower()[:16]
    stored_name = f"{uuid4().hex}{suffix}"
    return (
        f"leads/{instance.message.conversation.lead_id}/"
        f"messages/{instance.message_id}/{stored_name}"
    )


class LeadMessageAttachment(BaseModel):
    message = models.ForeignKey(
        LeadMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        upload_to=lead_message_attachment_upload_path,
        max_length=500,
    )
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


class LeadMessageRead(BaseModel):
    message = models.ForeignKey(
        LeadMessage,
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("message", "user"),
                name="unique_lead_message_read",
            ),
        )

    def __str__(self):
        return f"{self.user} read {self.message_id}"
