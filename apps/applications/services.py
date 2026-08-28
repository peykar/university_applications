from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

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
) -> Application:
    """Create a formal draft application for a concrete program offering."""
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

    return application
