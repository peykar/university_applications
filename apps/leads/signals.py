from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadConversation,
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
    LeadConversation.objects.get_or_create(
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
        is_customer_visible=True,
        created_by=instance.created_by,
        updated_by=instance.updated_by,
    )
