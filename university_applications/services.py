from __future__ import annotations

from django.db import transaction

from .models import Application, ProgramOffering, Student


@transaction.atomic
def create_application_from_offering(
    *,
    student: Student,
    offering: ProgramOffering,
    agent=None,
    created_by=None,
    notes: str = "",
) -> Application:
    """Create an application with tuition/deposit snapshots from the offering."""
    tuition = offering.tuition_discounted or offering.tuition
    return Application.objects.create(
        student=student,
        agent=agent or student.agent,
        program_offering=offering,
        tuition=tuition,
        deposit=offering.deposit,
        notes=notes,
        created_by=created_by,
        updated_by=created_by,
    )
