from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import translation

from apps.accounts.adapters import TurkDemyAccountAdapter


@dataclass(frozen=True)
class EmailPreviewSpec:
    key: str
    label: str
    template_prefix: str
    category: str


EMAIL_PREVIEW_REGISTRY: dict[str, EmailPreviewSpec] = {
    "login_code": EmailPreviewSpec(
        key="login_code",
        label="Sign-in code",
        template_prefix="account/email/login_code",
        category="Authentication",
    ),
    "email_confirmation_signup": EmailPreviewSpec(
        key="email_confirmation_signup",
        label="Signup email verification",
        template_prefix="account/email/email_confirmation_signup",
        category="Authentication",
    ),
    "email_confirmation": EmailPreviewSpec(
        key="email_confirmation",
        label="Email verification",
        template_prefix="account/email/email_confirmation",
        category="Authentication",
    ),
    "account_already_exists": EmailPreviewSpec(
        key="account_already_exists",
        label="Account already exists",
        template_prefix="account/email/account_already_exists",
        category="Authentication",
    ),
    "unknown_account": EmailPreviewSpec(
        key="unknown_account",
        label="Unknown account",
        template_prefix="account/email/unknown_account",
        category="Authentication",
    ),
    "password_reset_key": EmailPreviewSpec(
        key="password_reset_key",
        label="Password reset link",
        template_prefix="account/email/password_reset_key",
        category="Security",
    ),
    "password_reset_code": EmailPreviewSpec(
        key="password_reset_code",
        label="Password reset code",
        template_prefix="account/email/password_reset_code",
        category="Security",
    ),
    "password_reset": EmailPreviewSpec(
        key="password_reset",
        label="Password reset completed",
        template_prefix="account/email/password_reset",
        category="Security",
    ),
    "password_changed": EmailPreviewSpec(
        key="password_changed",
        label="Password changed",
        template_prefix="account/email/password_changed",
        category="Security",
    ),
    "password_set": EmailPreviewSpec(
        key="password_set",
        label="Password set",
        template_prefix="account/email/password_set",
        category="Security",
    ),
    "email_changed": EmailPreviewSpec(
        key="email_changed",
        label="Email changed",
        template_prefix="account/email/email_changed",
        category="Security",
    ),
    "email_confirm": EmailPreviewSpec(
        key="email_confirm",
        label="Email confirmed",
        template_prefix="account/email/email_confirm",
        category="Security",
    ),
    "email_deleted": EmailPreviewSpec(
        key="email_deleted",
        label="Email removed",
        template_prefix="account/email/email_deleted",
        category="Security",
    ),
}


def registered_template_prefixes() -> set[str]:
    return {spec.template_prefix for spec in EMAIL_PREVIEW_REGISTRY.values()}


def is_registered_email_type(email_type: str) -> bool:
    return email_type in EMAIL_PREVIEW_REGISTRY


def sample_email_context() -> dict[str, Any]:
    user_model = get_user_model()
    user = user_model(
        username="sample.student",
        email="student@example.com",
        first_name="Sample",
        last_name="Student",
    )
    current_site = SimpleNamespace(
        domain="turkdemy.com",
        name="TurkDemy",
    )
    return {
        "user": user,
        "email": "student@example.com",
        "current_site": current_site,
        "site_name": "TurkDemy",
        "site_domain": "turkdemy.com",
        "code": "48317",
        "key": "sample-verification-key",
        "activate_url": "https://turkdemy.com/accounts/confirm-email/sample/",
        "signup_url": "https://turkdemy.com/accounts/signup/",
        "password_reset_url": "https://turkdemy.com/accounts/password/reset/",
        "password_reset_key_url": ("https://turkdemy.com/accounts/password/reset/key/sample/"),
        "from_email": "old-address@example.com",
        "to_email": "student@example.com",
        "deleted_email": "old-address@example.com",
        "confirmed_email": "student@example.com",
        "ip": "203.0.113.42",
        "user_agent": "Mozilla/5.0 (Email Preview)",
        "timestamp": datetime(2026, 8, 26, 9, 30, tzinfo=UTC),
    }


def render_email_preview(
    *,
    email_type: str,
    language: str,
):
    spec = EMAIL_PREVIEW_REGISTRY[email_type]
    with translation.override(language):
        adapter = TurkDemyAccountAdapter()
        message = adapter.render_mail(
            spec.template_prefix,
            "student@example.com",
            sample_email_context(),
        )

    html_body = ""
    alternatives = getattr(message, "alternatives", [])
    for alternative in alternatives:
        mimetype = getattr(alternative, "mimetype", None) or alternative[1]
        if mimetype == "text/html":
            html_body = getattr(alternative, "content", None) or alternative[0]
            break

    return {
        "spec": spec,
        "language": language,
        "subject": str(message.subject),
        "text_body": str(message.body),
        "html_body": str(html_body),
        "message": message,
    }
