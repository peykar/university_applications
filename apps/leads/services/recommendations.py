from __future__ import annotations

from django.db.models import Exists, OuterRef, Q

from apps.core.audit import get_system_user
from apps.universities.models import Program, ProgramOffering

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadProgramInterestStatus,
    LeadStatus,
)
from .messaging import send_system_message


def _matching_offerings(lead: Lead):
    preferences = lead.preferences
    offerings = ProgramOffering.objects.filter(
        is_active=True,
        program__is_active=True,
        program__university__is_active=True,
    ).select_related("program")

    if preferences.tuition_min is not None:
        offerings = offerings.filter(tuition__gte=preferences.tuition_min)
    if preferences.tuition_max is not None:
        offerings = offerings.filter(tuition__lte=preferences.tuition_max)
    if preferences.tuition_currency:
        offerings = offerings.filter(currency=preferences.tuition_currency)

    return offerings


def recommend_programs_for_lead(
    lead: Lead,
    *,
    limit: int = 10,
    performed_by=None,
) -> list[LeadProgramInterest]:
    """
    Create system-suggested program interests from broad LeadPreference data.

    This is deterministic filtering, not an opaque ranking/AI decision.
    Staff can review all suggestions before qualification/conversion.
    """
    actor = performed_by or get_system_user()
    preferences = lead.preferences

    programs = Program.objects.filter(
        is_active=True,
        university__is_active=True,
    ).select_related(
        "university",
        "department",
        "program_language",
    )

    degrees = preferences.preferred_degrees or []
    if degrees:
        programs = programs.filter(degree__in=degrees)

    university_types = preferences.preferred_university_types or []
    if university_types:
        programs = programs.filter(university__university_type__in=university_types)

    language_ids = list(preferences.preferred_languages.values_list("id", flat=True))
    if language_ids:
        programs = programs.filter(program_language_id__in=language_ids)

    city_ids = list(preferences.preferred_cities.values_list("id", flat=True))
    if city_ids:
        programs = programs.filter(university__city_id__in=city_ids)

    university_ids = list(
        preferences.preferred_universities.values_list("id", flat=True)
    )
    if university_ids:
        programs = programs.filter(university_id__in=university_ids)

    department_names = list(
        preferences.preferred_departments.values_list("name_en", flat=True)
    )
    if department_names:
        programs = programs.filter(department__name_en__in=department_names)

    if preferences.requires_dormitory is True:
        programs = programs.filter(university__has_dormitory=True)
    if preferences.requires_erasmus is True:
        programs = programs.filter(university__has_erasmus=True)

    has_tuition_filter = any(
        (
            preferences.tuition_min is not None,
            preferences.tuition_max is not None,
            bool(preferences.tuition_currency),
        )
    )

    matching_offerings = _matching_offerings(lead)
    if has_tuition_filter:
        correlated = matching_offerings.filter(program_id=OuterRef("pk"))
        programs = programs.annotate(
            has_matching_offering=Exists(correlated)
        ).filter(has_matching_offering=True)

    programs = programs.order_by(
        "-listing_priority",
        "university__name_en",
        "name_en",
    ).distinct()

    created: list[LeadProgramInterest] = []

    for program in programs[: max(limit * 3, limit)]:
        if len(created) >= limit:
            break

        if LeadProgramInterest.objects.filter(
            lead=lead,
            program=program,
        ).exclude(status=LeadProgramInterestStatus.DECLINED).exists():
            continue

        offering = (
            matching_offerings.filter(program=program)
            .order_by("tuition", "deadline")
            .first()
        )

        interest = LeadProgramInterest.objects.create(
            lead=lead,
            program=program,
            program_offering=offering,
            source=LeadProgramInterestSource.SYSTEM,
            status=LeadProgramInterestStatus.SUGGESTED,
            suggested_by=performed_by,
            suggestion_reason="Matched the applicant's saved study preferences.",
            created_by=actor,
            updated_by=actor,
        )
        created.append(interest)

    if created:
        if lead.status not in {LeadStatus.CONVERTED, LeadStatus.REJECTED}:
            lead.status = LeadStatus.RECOMMENDATIONS_SENT
            lead.updated_by = actor
            lead.save(update_fields=("status", "updated_by", "updated_at"))

        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivityType.RECOMMENDATIONS_GENERATED,
            description=f"{len(created)} program recommendation(s) generated.",
            is_customer_visible=True,
            created_by=actor,
            updated_by=actor,
        )
        send_system_message(
            lead,
            f"We suggested {len(created)} program(s) based on the saved study preferences. "
            "Please review them and tell us which ones you like.",
            performed_by=actor,
        )

    return created
