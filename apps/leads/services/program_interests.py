from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _

from apps.universities.models import Program, ProgramOffering

from ..models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadStatus,
)


@dataclass(frozen=True)
class CustomerProgramInterestResult:
    interest: LeadProgramInterest
    created: bool
    reopened: bool


@transaction.atomic
def add_customer_program_interest(
    *,
    lead: Lead,
    program: Program,
    offering: ProgramOffering | None,
    performed_by,
) -> CustomerProgramInterestResult:
    """Add one genuinely new customer program and reopen a finalized Request."""
    locked_lead = Lead.objects.select_for_update().get(pk=lead.pk)
    if locked_lead.status == LeadStatus.CLOSED:
        raise ValidationError(_("A closed Request must be reopened by TurkDemy first."))

    existing = (
        LeadProgramInterest.objects.select_for_update()
        .filter(lead=locked_lead, program=program)
        .order_by("created_at", "pk")
        .first()
    )
    if existing is not None:
        return CustomerProgramInterestResult(existing, created=False, reopened=False)

    if offering is not None and offering.program_id != program.pk:
        raise ValidationError(_("The selected intake must belong to this program."))

    interest = LeadProgramInterest.objects.create(
        lead=locked_lead,
        program=program,
        program_offering=offering,
        source=LeadProgramInterestSource.USER,
        created_by=performed_by,
        updated_by=performed_by,
    )

    reopened = locked_lead.status == LeadStatus.FINALIZED
    if reopened:
        if not locked_lead.converted_student_id:
            raise ValidationError(_("This completed Request has no Student record to reopen."))
        locked_lead.status = LeadStatus.REOPENED
        locked_lead.updated_by = performed_by
        locked_lead.save(update_fields=("status", "updated_by", "updated_at"))
        LeadActivity.objects.create(
            lead=locked_lead,
            activity_type=LeadActivityType.REOPENED,
            description=_("Request reopened after a new program was added."),
            metadata={
                "action": "program_reopen",
                "program_id": str(program.pk),
                "interest_id": str(interest.pk),
            },
            is_customer_visible=True,
            created_by=performed_by,
            updated_by=performed_by,
        )
        lead.status = LeadStatus.REOPENED

    LeadActivity.objects.create(
        lead=locked_lead,
        activity_type=LeadActivityType.PROGRAM_ADDED,
        description=_("Program added: %(program)s.") % {"program": program.localized_name},
        metadata={
            "action": "program_added",
            "program_id": str(program.pk),
            "interest_id": str(interest.pk),
        },
        is_customer_visible=True,
        created_by=performed_by,
        updated_by=performed_by,
    )
    return CustomerProgramInterestResult(interest, created=True, reopened=reopened)
