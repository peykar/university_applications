from __future__ import annotations

from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from apps.applications.services import create_student_application
from apps.core.audit import get_system_user
from apps.messaging.models import SystemMessageEventType
from apps.students.models import Student, StudentDocument
from apps.universities.models import ProgramOffering

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocumentReviewHistory,
    LeadDocumentReviewStatus,
    LeadProgramInterest,
    LeadStatus,
)
from .messaging import send_system_message


def _copy_selected_documents(
    lead: Lead,
    student: Student,
    *,
    selected_document_ids: list[object],
    actor,
) -> list[StudentDocument]:
    selected = list(lead.documents.filter(pk__in=selected_document_ids).order_by("created_at"))
    if len(selected) != len(set(selected_document_ids)):
        raise ValidationError("One or more selected documents are invalid.")

    copied: list[StudentDocument] = []
    now = timezone.now()
    for source in selected:
        if not source.is_verified:
            source.review_status = LeadDocumentReviewStatus.APPROVED
            source.reviewed_by = actor
            source.reviewed_at = now
            source.review_note = "Approved during Student record creation."
            source.is_verified = True
            source.verified_by = actor
            source.verified_at = now
            source.updated_by = actor
            source.save(
                update_fields=(
                    "review_status",
                    "reviewed_by",
                    "reviewed_at",
                    "review_note",
                    "is_verified",
                    "verified_by",
                    "verified_at",
                    "updated_by",
                    "updated_at",
                )
            )
            LeadDocumentReviewHistory.objects.create(
                document=source,
                review_status=LeadDocumentReviewStatus.APPROVED,
                review_note=source.review_note,
                reviewed_by=actor,
                reviewed_at=now,
                created_by=actor,
                updated_by=actor,
            )
            LeadActivity.objects.create(
                lead=lead,
                activity_type=LeadActivityType.DOCUMENT_REVIEWED,
                description=(
                    f"Document approved during Student record creation: "
                    f"{source.name or source.get_document_type_display()}."
                ),
                metadata={
                    "action": "student_conversion_approved",
                    "document_name": source.name,
                    "document_type": source.document_type,
                },
                is_customer_visible=True,
                created_by=actor,
                updated_by=actor,
            )

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
        target.file.save(Path(source.file.name).name, content, save=False)
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


def _student_data_from_lead(lead: Lead) -> dict[str, object]:
    fields = (
        "first_name",
        "middle_name",
        "last_name",
        "country_of_birth",
        "nationality",
        "gender",
        "email",
        "cell",
        "birthdate",
        "english_test_type",
        "english_language_test_score",
        "high_school_gpa",
        "high_school_gpa_scale",
        "father_name",
        "mother_name",
        "passport_no",
        "passport_issuing_authority",
        "passport_date_of_issue",
        "passport_date_of_expiry",
        "country_of_residence",
        "city_of_residence",
        "address",
        "educational_background",
        "notes",
    )
    return {field: getattr(lead, field) for field in fields}


def _validate_application_selections(
    lead: Lead,
    selections: list[tuple[LeadProgramInterest, ProgramOffering]],
) -> None:
    seen_interest_ids: set[object] = set()
    seen_offering_ids: set[object] = set()
    for interest, offering in selections:
        if interest.lead_id != lead.pk:
            raise ValidationError("Every selected program must belong to this applicant.")
        if interest.pk in seen_interest_ids:
            raise ValidationError("A discussed program cannot be selected twice.")
        if offering.program_id != interest.program_id:
            raise ValidationError("The selected intake must belong to the discussed program.")
        if not offering.is_active:
            raise ValidationError("The selected intake is no longer active.")
        if offering.pk in seen_offering_ids:
            raise ValidationError("The same intake cannot create more than one draft application.")
        seen_interest_ids.add(interest.pk)
        seen_offering_ids.add(offering.pk)


@transaction.atomic
def finalize_lead(
    lead: Lead,
    *,
    application_selections: list[tuple[LeadProgramInterest, ProgramOffering]],
    student_data: dict[str, object] | None = None,
    selected_document_ids: list[object] | None = None,
    performed_by=None,
) -> Student:
    """
    Atomically finalize a Lead and create its canonical Student record.

    The agent-facing operation is deliberately one step: validate submitted Student
    data and any selected discussed programs, create the Student, copy selected
    documents, create draft Applications for any selections, link Lead -> Student,
    and mark the Lead FINALIZED. If any validation or persistence step fails, the transaction
    rolls back and the Lead remains in its previous lifecycle state.

    Safe to call again after successful conversion: an already converted Student
    is reused without creating duplicate Applications.
    """
    actor = performed_by or get_system_user()

    if lead.status == LeadStatus.CLOSED:
        raise ValidationError("A closed lead cannot be finalized.")
    if lead.converted_student_id and lead.status != LeadStatus.REOPENED:
        student = lead.converted_student
        if student is None:
            raise ValidationError("Converted student record could not be loaded.")
        return student

    _validate_application_selections(lead, application_selections)

    if lead.converted_student_id:
        student = lead.converted_student
        if student is None:
            raise ValidationError("Converted student record could not be loaded.")
        created_count = 0
        for _interest, offering in application_selections:
            duplicate = (
                student.applications.filter(
                    program_offering=offering,
                )
                .exclude(status__in=("rejected", "withdrawn", "cancelled"))
                .exists()
            )
            if duplicate:
                continue
            create_student_application(
                student=student,
                offering=offering,
                performed_by=actor,
            )
            created_count += 1

        now = timezone.now()
        lead.status = LeadStatus.FINALIZED
        lead.validated_by = actor
        lead.validated_at = now
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
            description=(
                f"Re-finalized existing Student {student.pk}; "
                f"created {created_count} new draft application(s)."
            ),
            metadata={
                "action": "refinalized",
                "student_id": str(student.pk),
                "new_application_count": created_count,
                "reopened": True,
            },
            is_customer_visible=True,
            created_by=actor,
            updated_by=actor,
        )
        send_system_message(
            lead,
            event_type=SystemMessageEventType.LEAD_FINALIZED,
            event_data={"student_id": str(student.pk)},
            performed_by=actor,
        )
        return student
    if student_data is None:
        student_data = _student_data_from_lead(lead)
    if selected_document_ids is None:
        selected_document_ids = list(
            lead.documents.filter(is_verified=True).values_list("pk", flat=True)
        )

    student = Student(
        user=lead.user,
        agent=lead.agent,
        created_by=actor,
        updated_by=actor,
        **student_data,
    )
    student.full_clean(exclude=("user", "agent", "created_by", "updated_by"))
    student.save()

    for _interest, offering in application_selections:
        create_student_application(
            student=student,
            offering=offering,
            performed_by=actor,
        )

    _copy_selected_documents(
        lead,
        student,
        selected_document_ids=selected_document_ids,
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
            f"created {len(application_selections)} draft application(s)."
        ),
        metadata={
            "action": "finalized",
            "student_id": str(student.pk),
            "new_application_count": len(application_selections),
            "reopened": False,
        },
        is_customer_visible=True,
        created_by=actor,
        updated_by=actor,
    )

    send_system_message(
        lead,
        event_type=SystemMessageEventType.LEAD_FINALIZED,
        event_data={"student_id": str(student.pk)},
        performed_by=actor,
    )

    return student


# Backward-compatible service alias for callers that still use the old name.
# There is no separate conversion phase anymore.
convert_lead_to_student = finalize_lead
