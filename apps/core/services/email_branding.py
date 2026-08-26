from __future__ import annotations

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

EMAIL_BRAND_NAMES = {
    "fa": "ترک‌دمی",
    "ar": "ترك ديمي",
}


def localized_email_brand_name(language: str | None = None) -> str:
    active_language = language or translation.get_language() or "en"
    language_code = active_language.split("-")[0].lower()
    return EMAIL_BRAND_NAMES.get(language_code, "TurkDemy")


def branded_email_context(
    *,
    subject: str,
    text_body: str,
) -> dict[str, str]:
    language = translation.get_language() or settings.LANGUAGE_CODE
    direction = "rtl" if language.split("-")[0] in {"fa", "ar"} else "ltr"
    site_url = settings.SITE_URL.rstrip("/")
    return {
        "email_subject": subject,
        "text_body": text_body,
        "brand_name": localized_email_brand_name(language),
        "email_language": language,
        "email_direction": direction,
        "site_url": site_url,
        "site_domain": site_url.removeprefix("https://").removeprefix("http://"),
    }


def render_branded_email_html(*, subject: str, text_body: str) -> str:
    return render_to_string(
        "emails/base.html",
        branded_email_context(subject=subject, text_body=text_body),
    )
