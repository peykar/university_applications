from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.students.models import Student
from apps.universities.models import OfferingFeeType, ProgramOffering

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

    tuition_fee = offering.display_tuition_fee
    if tuition_fee is None or tuition_fee.amount is None:
        raise ValidationError(
            "The selected program offering needs an active tuition fee before an "
            "application can be created."
        )
    deposit_fee = (
        offering.fees.filter(
            is_active=True,
            fee_type=OfferingFeeType.DEPOSIT,
            amount__isnull=False,
        )
        .order_by("created_at", "pk")
        .first()
    )

    application = Application.objects.create(
        student=student,
        agent=student.agent,
        program_offering=offering,
        status=ApplicationStatus.DRAFT,
        tuition=tuition_fee.amount,
        deposit=deposit_fee.amount if deposit_fee is not None else None,
        created_by=performed_by,
        updated_by=performed_by,
    )

    return application
