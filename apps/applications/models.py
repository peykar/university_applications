from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.agents.models import Agent
from apps.core.models import BaseModel
from apps.students.models import Student, StudentDocument
from apps.universities.models import ProgramOffering


class ApplicationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    UNDER_REVIEW = "under_review", _("Under Review")
    ADDITIONAL_DOCUMENTS = "additional_documents", _("Additional Documents Required")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    WITHDRAWN = "withdrawn", _("Withdrawn")
    CANCELLED = "cancelled", _("Cancelled")


class Application(BaseModel):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )
    program_offering = models.ForeignKey(
        ProgramOffering,
        on_delete=models.PROTECT,
        related_name="applications",
    )
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )
    tuition = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.program_offering}"


class ApplicationDocument(BaseModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    student_document = models.ForeignKey(
        StudentDocument,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    is_required = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if (
            self.student_document_id
            and self.application_id
            and self.student_document.student_id != self.application.student_id
        ):
            raise ValidationError(
                {"student_document": _("Document must belong to the application student.")}
            )
