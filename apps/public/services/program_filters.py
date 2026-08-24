from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db.models import Exists, Min, OuterRef, Q, QuerySet
from django.utils import timezone

from apps.universities.models import Program, ProgramOffering


@dataclass(frozen=True)
class ProgramFilterState:
    q: str = ""
    field: str = ""
    degree: str = ""
    language: str = ""
    university: str = ""
    city: str = ""
    university_type: str = ""
    tuition_min: str = ""
    tuition_max: str = ""
    currency: str = ""
    academic_year: str = ""
    semester: str = ""
    open_only: bool = False
    moe: bool = False
    moh: bool = False
    yok: bool = False
    erasmus: bool = False


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _decimal(value: str | None) -> Decimal | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def read_program_filters(params: Any) -> ProgramFilterState:
    return ProgramFilterState(
        q=(params.get("q") or "").strip(),
        field=(params.get("field") or "").strip(),
        degree=(params.get("degree") or "").strip(),
        language=(params.get("language") or "").strip(),
        university=(params.get("university") or "").strip(),
        city=(params.get("city") or "").strip(),
        university_type=(params.get("university_type") or "").strip(),
        tuition_min=(params.get("tuition_min") or "").strip(),
        tuition_max=(params.get("tuition_max") or "").strip(),
        currency=(params.get("currency") or "").strip(),
        academic_year=(params.get("academic_year") or "").strip(),
        semester=(params.get("semester") or "").strip(),
        open_only=_truthy(params.get("open")),
        moe=_truthy(params.get("moe")),
        moh=_truthy(params.get("moh")),
        yok=_truthy(params.get("yok")),
        erasmus=_truthy(params.get("erasmus")),
    )


def apply_program_filters(
    queryset: QuerySet[Program],
    state: ProgramFilterState,
) -> QuerySet[Program]:
    """
    Apply programme-level and offering-level filters.

    All offering-related criteria are applied to one correlated
    ProgramOffering subquery. This prevents false matches where, for example,
    the requested semester belongs to one offering but the requested tuition
    belongs to another.
    """
    if state.q:
        queryset = queryset.filter(
            Q(name_en__icontains=state.q)
            | Q(name_fa__icontains=state.q)
            | Q(name_tr__icontains=state.q)
            | Q(name_ar__icontains=state.q)
            | Q(university__name_en__icontains=state.q)
            | Q(university__name_fa__icontains=state.q)
            | Q(university__name_tr__icontains=state.q)
            | Q(department__name_en__icontains=state.q)
            | Q(department__name_fa__icontains=state.q)
            | Q(department__name_tr__icontains=state.q)
        )

    if state.field:
        queryset = queryset.filter(department__name_en=state.field)

    if state.degree:
        queryset = queryset.filter(degree=state.degree)

    if state.language:
        queryset = queryset.filter(program_language_id=state.language)

    if state.university:
        queryset = queryset.filter(university_id=state.university)

    if state.city:
        queryset = queryset.filter(university__city_id=state.city)

    if state.university_type:
        queryset = queryset.filter(university__university_type=state.university_type)

    if state.moe:
        queryset = queryset.filter(university__is_moe_approved=True)

    if state.moh:
        queryset = queryset.filter(university__is_moh_approved=True)

    if state.yok:
        queryset = queryset.filter(university__is_yok_recognized=True)

    if state.erasmus:
        queryset = queryset.filter(university__has_erasmus=True)

    tuition_min = _decimal(state.tuition_min)
    tuition_max = _decimal(state.tuition_max)

    has_offering_filter = any(
        (
            tuition_min is not None,
            tuition_max is not None,
            state.currency,
            state.academic_year,
            state.semester,
            state.open_only,
        )
    )

    if has_offering_filter:
        offerings = ProgramOffering.objects.filter(
            program_id=OuterRef("pk"),
            is_active=True,
        )

        if tuition_min is not None:
            offerings = offerings.filter(tuition__gte=tuition_min)

        if tuition_max is not None:
            offerings = offerings.filter(tuition__lte=tuition_max)

        if state.currency:
            offerings = offerings.filter(currency=state.currency)

        if state.academic_year:
            offerings = offerings.filter(academic_year_id=state.academic_year)

        if state.semester:
            offerings = offerings.filter(semester_id=state.semester)

        if state.open_only:
            today = timezone.localdate()
            offerings = offerings.filter(
                Q(deadline__isnull=True) | Q(deadline__gte=today)
            )

        queryset = queryset.annotate(
            matching_offering=Exists(offerings)
        ).filter(matching_offering=True)

    return queryset.annotate(
        min_active_tuition=Min(
            "offerings__tuition",
            filter=Q(offerings__is_active=True),
        )
    ).distinct()
