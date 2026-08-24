from __future__ import annotations

from typing import Any

from allauth.account.models import EmailAddress
from django.db import transaction

from .models import User


def google_verified_email(extra_data: dict[str, Any] | None) -> str | None:
    """Return Google's email only when Google explicitly marks it verified."""
    data = extra_data or {}
    email = str(data.get("email") or "").strip().lower()
    verified = data.get("email_verified")

    # Google's OIDC payload normally uses email_verified=True. Some allauth
    # payloads/providers serialize it as a string, so accept the true spelling.
    is_verified = verified is True or (isinstance(verified, str) and verified.lower() == "true")
    return email if email and is_verified else None


@transaction.atomic
def ensure_verified_login_email(user: User, email: str) -> EmailAddress:
    """
    Synchronize a trusted provider-verified email into django-allauth.

    Never moves an EmailAddress from another user and never overwrites a
    different user's canonical email.
    """
    email = email.strip().lower()

    foreign_address = EmailAddress.objects.filter(email__iexact=email).exclude(user=user).first()
    if foreign_address is not None:
        return foreign_address

    address, _ = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
        defaults={"verified": True, "primary": False},
    )

    update_fields: list[str] = []
    if not address.verified:
        address.verified = True
        update_fields.append("verified")

    has_other_primary = (
        EmailAddress.objects.filter(user=user, primary=True).exclude(pk=address.pk).exists()
    )
    if not has_other_primary and not address.primary:
        address.primary = True
        update_fields.append("primary")

    if update_fields:
        address.save(update_fields=update_fields)

    # Keep User.email aligned when there is no canonical email yet or this is
    # the primary allauth address. Do not silently replace a different email.
    if address.primary and not user.email:
        user.email = email
        user.save(update_fields=["email"])

    return address
