from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured


def get_system_user():
    """Return the non-human account used by automated jobs and imports.

    Identity and permissions are configured through Django settings, which are
    populated from environment variables in ``turkdemy.settings.base``.
    """

    User = get_user_model()
    username = settings.SYSTEM_USER_USERNAME
    email = settings.SYSTEM_USER_EMAIL

    if not username:
        raise ImproperlyConfigured("SYSTEM_USER_USERNAME must not be empty.")
    if not email:
        raise ImproperlyConfigured("SYSTEM_USER_EMAIL must not be empty.")
    if settings.SYSTEM_USER_IS_SUPERUSER and not settings.SYSTEM_USER_IS_STAFF:
        raise ImproperlyConfigured("SYSTEM_USER_IS_SUPERUSER=1 requires SYSTEM_USER_IS_STAFF=1.")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_active": settings.SYSTEM_USER_IS_ACTIVE,
            "is_staff": settings.SYSTEM_USER_IS_STAFF,
            "is_superuser": settings.SYSTEM_USER_IS_SUPERUSER,
        },
    )

    changed_fields: list[str] = []

    if created:
        user.set_unusable_password()
        changed_fields.append("password")
    elif user.has_usable_password():
        raise ImproperlyConfigured(
            "The configured SYSTEM_USER_USERNAME belongs to a login-capable user. "
            "Choose a dedicated non-human username instead."
        )

    desired = {
        "email": email,
        "is_active": settings.SYSTEM_USER_IS_ACTIVE,
        "is_staff": settings.SYSTEM_USER_IS_STAFF,
        "is_superuser": settings.SYSTEM_USER_IS_SUPERUSER,
    }
    for field_name, desired_value in desired.items():
        if getattr(user, field_name) != desired_value:
            setattr(user, field_name, desired_value)
            changed_fields.append(field_name)

    if changed_fields:
        user.save(update_fields=sorted(set(changed_fields)))

    return user


def audited_update_or_create(
    manager: Any,
    *,
    lookup: dict[str, Any],
    defaults: dict[str, Any],
    actor=None,
):
    """update_or_create while preserving the original creator.

    Existing records receive ``updated_by=actor``. New records receive both
    ``created_by`` and ``updated_by``. The caller's defaults are not mutated.
    """

    actor = actor or get_system_user()
    update_defaults = {**defaults, "updated_by": actor}
    create_defaults = {
        **defaults,
        "created_by": actor,
        "updated_by": actor,
    }
    return manager.update_or_create(
        **lookup,
        defaults=update_defaults,
        create_defaults=create_defaults,
    )


def audited_get_or_create(
    manager: Any,
    *,
    lookup: dict[str, Any],
    defaults: dict[str, Any] | None = None,
    actor=None,
):
    """get_or_create with audit fields populated only when creating."""

    actor = actor or get_system_user()
    create_defaults = {
        **(defaults or {}),
        "created_by": actor,
        "updated_by": actor,
    }
    return manager.get_or_create(**lookup, defaults=create_defaults)
