from __future__ import annotations

from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application, ApplicationStatus
from apps.core.audit import get_system_user
from apps.students.models import Student, StudentDocument

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadProgramInterestStatus,
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

    if errors:
        raise ValidationError(errors)


@transaction.atomic
def finalize_lead(lead: Lead, *, performed_by=None) -> Lead:
    actor = performed_by or get_system_user()
    _validate_for_finalization(lead)

    lead.status = LeadStatus.FINALIZED
    lead.validated_by = actor
    lead.validated_at = timezone.now()
    lead.updated_by = actor
    lead.save(
        update_fields=(
            "status",
            "validated_by",
            "validated_at",
            "updated_by",
            "updated_at",
        )
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.FINALIZED,
        description="Applicant data validated and finalized.",
        is_customer_visible=True,
        created_by=actor,
        updated_by=actor,
    )

    send_system_message(
        lead,
        "Your applicant profile has been finalized and is ready for conversion.",
        performed_by=actor,
    )
    return lead


def _copy_verified_documents(
    lead: Lead,
    student: Student,
    *,
    actor,
) -> list[StudentDocument]:
    copied = []

    for source in lead.documents.filter(is_verified=True):
        if source.converted_student_document_id:
            copied.append(source.converted_student_document)
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


def _create_applications(
    lead: Lead,
    student: Student,
    *,
    actor,
) -> list[Application]:
    applications = []

    qualified = lead.program_interests.filter(
        status=LeadProgramInterestStatus.QUALIFIED,
    ).select_related(
        "program",
        "program_offering",
    )

    missing_offering = [
        interest.program.name_en
        for interest in qualified
        if interest.program_offering_id is None
    ]
    if missing_offering:
        raise ValidationError(
            {
                "program_interests": (
                    "Qualified program interests need a specific offering before "
                    "conversion: " + ", ".join(missing_offering)
                )
            }
        )

    for interest in qualified:
        if interest.converted_application_id:
            applications.append(interest.converted_application)
            continue

        offering = interest.program_offering
        tuition = (
            offering.tuition_discounted
            if offering.tuition_discounted is not None
            else offering.tuition
        )

        application = Application.objects.create(
            student=student,
            agent=lead.agent,
            program_offering=offering,
            status=ApplicationStatus.DRAFT,
            tuition=tuition,
            deposit=offering.deposit,
            notes=interest.notes,
            created_by=actor,
            updated_by=actor,
        )

        interest.converted_application = application
        interest.status = LeadProgramInterestStatus.CONVERTED
        interest.updated_by = actor
        interest.save(
            update_fields=(
                "converted_application",
                "status",
                "updated_by",
                "updated_at",
            )
        )
        applications.append(application)

    return applications


@transaction.atomic
def convert_lead_to_student(
    lead: Lead,
    *,
    performed_by=None,
) -> Student:
    """
    Convert a finalized Lead into the canonical Student record.

    Safe to call again: an already converted student is reused and any newly
    qualified program interests can still be converted into applications.
    """
    actor = performed_by or get_system_user()

    if lead.status not in {LeadStatus.FINALIZED, LeadStatus.CONVERTED}:
        raise ValidationError(
            "Lead must be finalized before it can be converted to a student."
        )

    _validate_for_finalization(lead)

    student = lead.converted_student

    if student is None:
        student = Student.objects.create(
            user=lead.user,
            agent=lead.agent,
            first_name=lead.first_name,
            middle_name=lead.middle_name,
            last_name=lead.last_name,
            country_of_birth=lead.country_of_birth,
            nationality=lead.nationality,
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

        lead.converted_student = student

    _copy_verified_documents(lead, student, actor=actor)
    applications = _create_applications(lead, student, actor=actor)

    lead.status = LeadStatus.CONVERTED
    lead.converted_at = lead.converted_at or timezone.now()
    lead.updated_by = actor
    lead.save(
        update_fields=(
            "converted_student",
            "status",
            "converted_at",
            "updated_by",
            "updated_at",
        )
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.CONVERTED,
        description=(
            f"Converted to Student {student.pk}; "
            f"{len(applications)} application(s) created/linked."
        ),
        is_customer_visible=True,
        created_by=actor,
        updated_by=actor,
    )

    send_system_message(
        lead,
        "Your finalized applicant profile has been converted to a student record.",
        performed_by=actor,
    )

    return student
