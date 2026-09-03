from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.agents.models import Agent

from .models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadPreference,
)


@receiver(post_save, sender=Lead)
def create_lead_workspace(sender, instance, created, **kwargs):
    if not created:
        return

    LeadPreference.objects.get_or_create(
        lead=instance,
        defaults={
            "created_by": instance.created_by,
            "updated_by": instance.updated_by,
        },
    )
    LeadActivity.objects.create(
        lead=instance,
        activity_type=LeadActivityType.CREATED,
        description="Applicant profile created.",
        metadata={"action": "profile_created"},
        is_customer_visible=True,
        created_by=instance.created_by,
        updated_by=instance.updated_by,
    )


@receiver(pre_save, sender=Lead)
def assign_default_agent(sender, instance, **kwargs):
    """Apply DEFAULT_LEAD_AGENT_ID to new leads that have no explicit agent."""
    if not instance._state.adding or instance.agent_id:
        return

    default_agent_id = settings.DEFAULT_LEAD_AGENT_ID
    if not default_agent_id:
        return

    default_agent = Agent.objects.filter(
        pk=default_agent_id,
        is_active=True,
    ).first()
    if default_agent is not None:
        instance.agent = default_agent
