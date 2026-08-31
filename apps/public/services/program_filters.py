from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from django.db.models import Exists, OuterRef, Q, QuerySet, Subquery
from django.utils import timezone

from apps.universities.models import OfferingFee, OfferingFeeType, Program, ProgramOffering


@dataclass(frozen=True)
class ProgramFilterState:
    q: str = ""
    field: str = ""
    degree: str = ""
    language: str = ""
    study_mode: str = ""
    academic_unit: str = ""
    university: str = ""
    city: str = ""
    university_type: str = ""
    tuition_min: str = ""
    tuition_max: str = ""
    currency: str = ""
    academic_year: str = ""
    intake: str = ""
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


def _uuid(value: str | None) -> UUID | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


def read_program_filters(params: Any) -> ProgramFilterState:
    return ProgramFilterState(
        q=(params.get("q") or "").strip(),
        field=(params.get("field") or "").strip(),
        degree=(params.get("degree") or "").strip(),
        language=(params.get("language") or "").strip(),
        study_mode=(params.get("study_mode") or "").strip(),
        academic_unit=(params.get("academic_unit") or "").strip(),
        university=(params.get("university") or "").strip(),
        city=(params.get("city") or "").strip(),
        university_type=(params.get("university_type") or "").strip(),
        tuition_min=(params.get("tuition_min") or "").strip(),
        tuition_max=(params.get("tuition_max") or "").strip(),
        currency=(params.get("currency") or "").strip(),
        academic_year=(params.get("academic_year") or "").strip(),
        intake=(params.get("intake") or "").strip(),
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
    ProgramOffering subquery. The displayed minimum tuition and currency are
    also selected from the same offering, so a price is never shown without
    (or with the wrong) currency.
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
        queryset = queryset.filter(department__slug_en=state.field)

    if state.degree:
        queryset = queryset.filter(degree=state.degree)

    if state.language:
        queryset = queryset.filter(instruction_languages__slug_en=state.language)

    if state.study_mode:
        queryset = queryset.filter(study_mode=state.study_mode)

    if state.academic_unit:
        queryset = queryset.filter(academic_unit__slug_en=state.academic_unit)

    if state.university:
        queryset = queryset.filter(university__slug_en=state.university)

    if state.city:
        queryset = queryset.filter(university__city__slug_en=state.city)

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

    offerings = ProgramOffering.objects.filter(
        program_id=OuterRef("pk"),
        is_active=True,
    )

    canonical_tuition = OfferingFee.objects.filter(
        offering_id=OuterRef("pk"),
        is_active=True,
        fee_type__in=(OfferingFeeType.DISCOUNTED_TUITION, OfferingFeeType.TUITION),
        amount__isnull=False,
    ).order_by("amount", "pk")
    offerings = offerings.annotate(
        canonical_tuition=Subquery(canonical_tuition.values("amount")[:1]),
        canonical_currency=Subquery(canonical_tuition.values("currency")[:1]),
    )

    if tuition_min is not None:
        offerings = offerings.filter(canonical_tuition__gte=tuition_min)

    if tuition_max is not None:
        offerings = offerings.filter(canonical_tuition__lte=tuition_max)

    if state.currency:
        offerings = offerings.filter(canonical_currency=state.currency)

    if state.academic_year:
        academic_year_id = _uuid(state.academic_year)
        if academic_year_id is None:
            return queryset.none()
        offerings = offerings.filter(academic_year_id=academic_year_id)

    if state.intake:
        intake_id = _uuid(state.intake)
        if intake_id is None:
            return queryset.none()
        offerings = offerings.filter(intake_id=intake_id)

    if state.open_only:
        today = timezone.localdate()
        offerings = offerings.filter(Q(deadline__isnull=True) | Q(deadline__gte=today))

    has_offering_filter = any(
        (
            tuition_min is not None,
            tuition_max is not None,
            state.currency,
            state.academic_year,
            state.intake,
            state.open_only,
        )
    )

    if has_offering_filter:
        queryset = queryset.annotate(matching_offering=Exists(offerings)).filter(
            matching_offering=True
        )

    cheapest_fee = OfferingFee.objects.filter(
        offering__program_id=OuterRef("pk"),
        offering__is_active=True,
        is_active=True,
        fee_type__in=(OfferingFeeType.DISCOUNTED_TUITION, OfferingFeeType.TUITION),
        amount__isnull=False,
    ).order_by("amount", "pk")

    return queryset.annotate(
        min_active_tuition=Subquery(cheapest_fee.values("amount")[:1]),
        min_active_currency=Subquery(cheapest_fee.values("currency")[:1]),
    ).distinct()


def annotate_min_active_tuition(
    queryset: QuerySet[Program],
) -> QuerySet[Program]:
    """Annotate Programs from canonical Catalogue v3 structured tuition fees."""
    cheapest_fee = OfferingFee.objects.filter(
        offering__program_id=OuterRef("pk"),
        offering__is_active=True,
        is_active=True,
        fee_type__in=(OfferingFeeType.DISCOUNTED_TUITION, OfferingFeeType.TUITION),
        amount__isnull=False,
    ).order_by("amount", "pk")
    return queryset.annotate(
        min_active_tuition=Subquery(cheapest_fee.values("amount")[:1]),
        min_active_currency=Subquery(cheapest_fee.values("currency")[:1]),
    )
