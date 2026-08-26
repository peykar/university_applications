from __future__ import annotations

from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application, ApplicationStatus
from apps.core.audit import get_system_user
from apps.core.phone import normalize_phone_number
from apps.students.models import Student, StudentDocument
from apps.universities.models import ProgramOffering

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadStatus,
)
from .messaging import send_system_message


def _validate_for_finalization(lead: Lead) -> None:
    errors = {}

    if not lead.first_name.strip():
        errors["first_name"] = "First name is required."
    if not lead.last_name.strip():
        errors["last_name"] = "Last name is required."
    if not lead.nationality_id:
        errors["nationality"] = "Nationality must be validated before finalization."
    if not lead.gender:
        errors["gender"] = "Gender must be validated before finalization."

    if lead.cell:
        try:
            normalize_phone_number(lead.cell)
        except ValueError:
            errors["cell"] = (
                "Enter a valid international phone number including the "
                "country code, for example +31612345678."
            )

    if errors:
        raise ValidationError(errors)


def _copy_verified_documents(
    lead: Lead,
    student: Student,
    *,
    actor,
) -> list[StudentDocument]:
    copied = []

    for source in lead.documents.filter(is_verified=True):
        if source.converted_student_document_id:
            converted_document = source.converted_student_document
            if converted_document is not None:
                copied.append(converted_document)
                continue

        source.file.open("rb")
        try:
            content = ContentFile(source.file.read())
        finally:
            source.file.close()

        target = StudentDocument(
            student=student,
            document_type=source.document_type,
            short_description=source.description or source.name,
            created_by=actor,
            updated_by=actor,
        )
        target.file.save(
            Path(source.file.name).name,
            content,
            save=False,
        )
        target.save()

        source.converted_student_document = target
        source.updated_by = actor
        source.save(
            update_fields=(
                "converted_student_document",
                "updated_by",
                "updated_at",
            )
        )
        copied.append(target)

    return copied


def _create_selected_draft_applications(
    lead: Lead,
    student: Student,
    *,
    selected_interest_ids: list[str] | tuple[str, ...],
    selected_offering_ids: dict[str, str] | None,
    actor,
) -> list[Application]:
    """Create Draft Applications from explicitly selected Lead interests."""
    if not selected_interest_ids:
        return []

    interests = list(
        lead.program_interests.select_related(
            "program",
            "program__university",
            "program_offering",
        ).filter(pk__in=selected_interest_ids)
    )

    if len(interests) != len(set(selected_interest_ids)):
        raise ValidationError("One or more selected programs do not belong to this applicant.")

    selected_offering_ids = selected_offering_ids or {}
    applications: list[Application] = []
    for interest in interests:
        offering = interest.program_offering
        selected_offering_id = selected_offering_ids.get(str(interest.pk), "")
        if selected_offering_id:
            try:
                offering = ProgramOffering.objects.get(
                    pk=selected_offering_id,
                    program=interest.program,
                    is_active=True,
                )
            except (ProgramOffering.DoesNotExist, ValueError):
                raise ValidationError(
                    {"programs": f"Choose a valid intake for {interest.program}."}
                ) from None

        if offering is None:
            raise ValidationError({"programs": f"Choose an intake for {interest.program}."})

        if interest.program_offering_id != offering.pk:
            interest.program_offering = offering
            interest.updated_by = actor
            interest.save(update_fields=("program_offering", "updated_by", "updated_at"))

        if interest.converted_application_id:
            converted = interest.converted_application
            if converted is not None:
                applications.append(converted)
                continue

        application = Application.objects.create(
            student=student,
            agent=lead.agent,
            program_offering=offering,
            status=ApplicationStatus.DRAFT,
            tuition=offering.tuition,
            deposit=offering.deposit,
            notes=interest.notes,
            created_by=actor,
            updated_by=actor,
        )
        interest.converted_application = application
        interest.updated_by = actor
        interest.save(
            update_fields=(
                "converted_application",
                "updated_by",
                "updated_at",
            )
        )
        applications.append(application)

    return applications


@transaction.atomic
def finalize_lead(
    lead: Lead,
    *,
    performed_by=None,
    selected_interest_ids: list[str] | tuple[str, ...] | None = None,
    selected_offering_ids: dict[str, str] | None = None,
) -> Student:
    """
    Atomically finalize a Lead and create its canonical Student record.

    The agent-facing operation is deliberately one step: validate the Lead,
    create the Student, copy verified documents, link Lead -> Student, and mark
    the Lead FINALIZED. If any validation or persistence step fails, the
    transaction rolls back and the Lead remains in its previous lifecycle
    state.

    Safe to call again: an already converted student is reused.

    Applicant program interests remain Lead history and are intentionally not
    converted into formal university applications.
    """
    actor = performed_by or get_system_user()
    selected_interest_ids = list(selected_interest_ids or [])

    if lead.status == LeadStatus.CLOSED:
        raise ValidationError("A closed lead cannot be finalized.")
    if lead.converted_student_id:
        student = lead.converted_student
        if student is None:
            raise ValidationError("Converted student record could not be loaded.")
        return student

    _validate_for_finalization(lead)

    nationality = lead.nationality
    if nationality is None:
        raise ValidationError("Nationality must be validated before finalization.")

    student = Student.objects.create(
        user=lead.user,
        agent=lead.agent,
        first_name=lead.first_name,
        middle_name=lead.middle_name,
        last_name=lead.last_name,
        country_of_birth=lead.country_of_birth,
        nationality=nationality,
        gender=lead.gender,
        email=lead.email,
        cell=lead.cell,
        birthdate=lead.birthdate,
        english_test_type=lead.english_test_type,
        english_language_test_score=lead.english_language_test_score,
        high_school_gpa=lead.high_school_gpa,
        high_school_gpa_scale=lead.high_school_gpa_scale,
        father_name=lead.father_name,
        mother_name=lead.mother_name,
        passport_no=lead.passport_no,
        passport_issuing_authority=lead.passport_issuing_authority,
        passport_date_of_issue=lead.passport_date_of_issue,
        passport_date_of_expiry=lead.passport_date_of_expiry,
        country_of_residence=lead.country_of_residence,
        city_of_residence=lead.city_of_residence,
        address=lead.address,
        educational_background=lead.educational_background,
        notes=lead.notes,
        created_by=actor,
        updated_by=actor,
    )

    _copy_verified_documents(lead, student, actor=actor)
    draft_applications = _create_selected_draft_applications(
        lead,
        student,
        selected_interest_ids=selected_interest_ids,
        selected_offering_ids=selected_offering_ids,
        actor=actor,
    )

    now = timezone.now()
    lead.converted_student = student
    lead.status = LeadStatus.FINALIZED
    lead.validated_by = actor
    lead.validated_at = now
    lead.converted_at = now
    lead.updated_by = actor
    lead.save(
        update_fields=(
            "converted_student",
            "status",
            "validated_by",
            "validated_at",
            "converted_at",
            "updated_by",
            "updated_at",
        )
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.FINALIZED,
        description=(
            f"Finalized and converted to Student {student.pk}; "
            f"{len(draft_applications)} draft application(s) created."
        ),
        is_customer_visible=True,
        created_by=actor,
        updated_by=actor,
    )

    send_system_message(
        lead,
        "Your applicant profile has been finalized and converted to a student record.",
        performed_by=actor,
    )

    return student


# Backward-compatible service alias for callers that still use the old name.
# There is no separate conversion phase anymore.
convert_lead_to_student = finalize_lead
