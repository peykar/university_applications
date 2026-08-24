from __future__ import annotations

from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=SocialAccount)
def sync_social_identity(sender, instance: SocialAccount, **kwargs) -> None:
    """Mirror useful Telegram identity fields onto TurkDemy's User model."""
    if instance.provider != "telegram":
        return

    user = instance.user
    if not isinstance(user, User):
        return

    extra_data = instance.extra_data or {}
    username = extra_data.get("username") or ""

    changed_fields: list[str] = []
    telegram_id = str(instance.uid)

    if user.telegram_id != telegram_id:
        user.telegram_id = telegram_id
        changed_fields.append("telegram_id")

    if username and user.telegram != username:
        user.telegram = username
        changed_fields.append("telegram")

    if changed_fields:
        user.save(update_fields=changed_fields)
