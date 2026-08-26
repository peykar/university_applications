from __future__ import annotations

from collections.abc import Iterable

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from ..email_previews import is_registered_email_type
from .email_branding import render_branded_email_html


def send_email(
    *,
    email_type: str,
    subject: str,
    to: str | Iterable[str],
    text_body: str,
    html_body: str | None = None,
    from_email: str | None = None,
) -> int:
    """
    Send a TurkDemy email using environment-driven Django email settings.
    """
    if not is_registered_email_type(email_type):
        raise ValueError(
            f"Outgoing email type {email_type!r} is not registered in EMAIL_PREVIEW_REGISTRY."
        )

    recipients = [to] if isinstance(to, str) else list(to)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )

    message.attach_alternative(
        html_body
        or render_branded_email_html(
            subject=subject,
            text_body=text_body,
        ),
        "text/html",
    )

    return message.send()
