from __future__ import annotations

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .social_email import ensure_verified_login_email, google_verified_email


@receiver(post_save, sender=SocialAccount)
def sync_social_identity(sender, instance: SocialAccount, **kwargs) -> None:
    """Mirror useful Telegram identity fields onto TurkDemy's User model."""
    user = instance.user
    if not isinstance(user, User):
        return

    extra_data = instance.extra_data or {}

    if instance.provider == "google":
        email = google_verified_email(extra_data)
        if not email:
            return

        # During a brand-new social signup, django-allauth saves SocialAccount
        # before setup_user_email(). Creating EmailAddress here would violate
        # allauth's invariant that the new user has no EmailAddress yet and
        # causes an AssertionError in setup_user_email().
        #
        # Existing/local-account connections may already have an EmailAddress;
        # in that case it is safe to normalize/verify that existing record.
        if EmailAddress.objects.filter(
            user=user,
            email__iexact=email,
        ).exists():
            ensure_verified_login_email(user, email)
        return

    if instance.provider != "telegram":
        return
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
