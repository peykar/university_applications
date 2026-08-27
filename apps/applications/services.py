from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.leads.models import LeadProgramInterest
from apps.students.models import Student
from apps.universities.models import ProgramOffering

from .models import Application, ApplicationStatus

INACTIVE_APPLICATION_STATUSES = (
    ApplicationStatus.REJECTED,
    ApplicationStatus.WITHDRAWN,
    ApplicationStatus.CANCELLED,
)


@transaction.atomic
def create_student_application(
    *,
    student: Student,
    offering: ProgramOffering,
    performed_by,
    source_interest: LeadProgramInterest | None = None,
) -> Application:
    """Create a formal draft application for a concrete program offering."""
    if source_interest is not None:
        source_lead = source_interest.lead
        if source_lead.converted_student_id != student.pk:
            raise ValidationError("The selected program interest does not belong to this student.")
        if source_interest.program_id != offering.program_id:
            raise ValidationError("The selected intake does not belong to the discussed program.")
        if source_interest.converted_application_id:
            raise ValidationError(
                "This discussed program has already been turned into an application."
            )

    duplicate = (
        Application.objects.filter(
            student=student,
            program_offering=offering,
        )
        .exclude(status__in=INACTIVE_APPLICATION_STATUSES)
        .exists()
    )
    if duplicate:
        raise ValidationError("An active application for this student and intake already exists.")

    application = Application.objects.create(
        student=student,
        agent=student.agent,
        program_offering=offering,
        status=ApplicationStatus.DRAFT,
        tuition=offering.tuition,
        deposit=offering.deposit,
        created_by=performed_by,
        updated_by=performed_by,
    )

    if source_interest is not None:
        source_interest.converted_application = application
        source_interest.updated_by = performed_by
        source_interest.save(
            update_fields=(
                "converted_application",
                "updated_by",
                "updated_at",
            )
        )

    return application
