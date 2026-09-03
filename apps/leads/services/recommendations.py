"""Program recommendation workflows for applicant leads.

Automatic/system-generated recommendations remain intentionally disabled. Agent-created
recommendations are handled here so the interest and its audit/message side effects share
one transactional boundary.
"""

from dataclasses import dataclass
from enum import StrEnum

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from apps.messaging.models import SystemMessageEventType

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadStatus,
)
from .messaging import send_system_message


class RecommendationOutcome(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    USER_INTEREST_EXISTS = "user_interest_exists"
    ALREADY_RECOMMENDED = "already_recommended"


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    interest: LeadProgramInterest
    outcome: RecommendationOutcome


def _validate_agent_recommendation(*, lead: Lead, program) -> None:
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        raise ValidationError(
            _(
                "Program recommendations cannot be changed after the applicant is "
                "finalized or closed."
            )
        )
    if not program.is_active or not program.university.is_active:
        raise ValidationError(_("Only active programs at active universities can be recommended."))


@transaction.atomic
def recommend_program(*, lead: Lead, program, agent_user, reason: str = "") -> RecommendationResult:
    """Create or update one agent recommendation for a program-level lead interest.

    A user-created interest is preserved unchanged. Creating a new agent recommendation
    also creates the customer-visible activity and structured system message in the same
    database transaction.
    """

    _validate_agent_recommendation(lead=lead, program=program)
    reason = reason.strip()

    interest = (
        LeadProgramInterest.objects.select_for_update()
        .filter(
            lead=lead,
            program=program,
            program_offering__isnull=True,
        )
        .first()
    )

    if interest is not None:
        if interest.source == LeadProgramInterestSource.USER:
            return RecommendationResult(
                interest=interest,
                outcome=RecommendationOutcome.USER_INTEREST_EXISTS,
            )

        changed = False
        if reason != interest.suggestion_reason:
            interest.suggestion_reason = reason
            interest.updated_by = agent_user
            changed = True
        if interest.suggested_by_id != agent_user.pk:
            interest.suggested_by = agent_user
            changed = True
        if changed:
            interest.save(
                update_fields=(
                    "suggestion_reason",
                    "suggested_by",
                    "updated_by",
                    "updated_at",
                )
            )
            return RecommendationResult(
                interest=interest,
                outcome=RecommendationOutcome.UPDATED,
            )

        return RecommendationResult(
            interest=interest,
            outcome=RecommendationOutcome.ALREADY_RECOMMENDED,
        )

    interest = LeadProgramInterest.objects.create(
        lead=lead,
        program=program,
        source=LeadProgramInterestSource.AGENT,
        suggested_by=agent_user,
        suggestion_reason=reason,
        created_by=agent_user,
        updated_by=agent_user,
    )
    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.PROGRAM_SUGGESTED,
        description=_("Program suggested: %(program)s.") % {"program": program.localized_name},
        metadata={
            "action": "program_suggested",
            "program_id": str(program.pk),
            "interest_id": str(interest.pk),
            "suggestion_reason": reason,
        },
        is_customer_visible=True,
        created_by=agent_user,
        updated_by=agent_user,
    )
    send_system_message(
        lead,
        event_type=SystemMessageEventType.PROGRAM_RECOMMENDED,
        event_data={
            "program_id": str(program.pk),
            "interest_id": str(interest.pk),
            "reason": reason,
        },
        performed_by=agent_user,
    )
    return RecommendationResult(
        interest=interest,
        outcome=RecommendationOutcome.CREATED,
    )


def recommend_programs_for_lead(*args, **kwargs):
    raise NotImplementedError(
        "Automatic/system program suggestions are disabled. "
        "Programs must be user-added or agent-suggested."
    )
