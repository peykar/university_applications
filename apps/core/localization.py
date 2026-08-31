from __future__ import annotations

from typing import Any

from django.conf import settings
from django.utils.translation import get_language


def normalized_language_code(language: str | None = None) -> str:
    """Return a supported two-letter locale code, falling back to English."""
    raw = (language or get_language() or settings.LANGUAGE_CODE or "en").lower()
    code = raw.replace("_", "-").split("-", 1)[0]
    supported = {item[0].split("-", 1)[0] for item in settings.LANGUAGES}
    return code if code in supported else "en"


def localized_value(obj: Any, field: str = "name", language: str | None = None) -> Any:
    """Prefer the active-locale field and fall back to canonical English.

    The helper is intentionally read-only: missing translations are never generated.
    It works with model instances and dictionaries so views/templates can share the
    same selection rule.
    """
    if obj is None:
        return ""

    code = normalized_language_code(language)
    candidates = (f"{field}_{code}", f"{field}_en")
    for key in candidates:
        value = obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)
        if value not in (None, ""):
            return value
    return ""
