from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django.conf import settings
from django.utils import timezone, translation
from django.utils.formats import date_format
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


_PERSIAN_MONTHS = (
    "",
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
)
_PERSIAN_DIGITS = str.maketrans(
    "0123456789",
    "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9",
)
_ARABIC_INDIC_DIGITS = str.maketrans(
    "0123456789",
    "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669",
)


def _gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    """Convert a Gregorian date to Solar Hijri without changing the stored value."""
    g_days_in_month = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    j_days_in_month = (31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29)

    gy = value.year
    gm = value.month
    gd = value.day
    gy_offset = gy - 1600
    gm_offset = gm - 1
    gd_offset = gd - 1

    g_day_no = (
        (365 * gy_offset)
        + ((gy_offset + 3) // 4)
        - ((gy_offset + 99) // 100)
        + ((gy_offset + 399) // 400)
    )
    g_day_no += sum(g_days_in_month[:gm_offset])
    is_gregorian_leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    if gm_offset > 1 and is_gregorian_leap:
        g_day_no += 1
    g_day_no += gd_offset

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + (33 * j_np) + (4 * (j_day_no // 1461))
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    jm = 1
    for days_in_month in j_days_in_month[:-1]:
        if j_day_no < days_in_month:
            break
        j_day_no -= days_in_month
        jm += 1

    return jy, jm, j_day_no + 1


def _localized_digits(value: str, language: str) -> str:
    if language == "fa":
        return value.translate(_PERSIAN_DIGITS)
    if language == "ar":
        return value.translate(_ARABIC_INDIC_DIGITS)
    return value


def _localized_django_date(value: date | datetime, format_string: str, language: str) -> str:
    with translation.override(language):
        return date_format(value, format_string)


def _presentation_datetime(value: datetime) -> datetime:
    if timezone.is_aware(value):
        return timezone.localtime(value)
    return value


def localized_date(value: date | datetime | None, language: str | None = None) -> str:
    """Render a human-facing date using the active locale's approved calendar."""
    if value is None or not isinstance(value, date):
        return ""

    code = normalized_language_code(language)
    display_value = _presentation_datetime(value) if isinstance(value, datetime) else value

    if code == "fa":
        gregorian_date = (
            display_value.date() if isinstance(display_value, datetime) else display_value
        )
        jy, jm, jd = _gregorian_to_jalali(gregorian_date)
        rendered = f"{jd} {_PERSIAN_MONTHS[jm]} {jy}"
        return _localized_digits(rendered, code)

    if code == "tr":
        rendered = _localized_django_date(display_value, "j M Y", code)
    elif code == "ar":
        rendered = _localized_django_date(display_value, "j F Y", code)
    else:
        rendered = _localized_django_date(display_value, "M j, Y", code)
    return _localized_digits(rendered, code)


def localized_time(value: datetime | None, language: str | None = None) -> str:
    """Render the time component without changing the represented instant."""
    if value is None or not isinstance(value, datetime):
        return ""

    code = normalized_language_code(language)
    display_value = _presentation_datetime(value)
    return _localized_digits(_localized_django_date(display_value, "H:i", code), code)


def localized_datetime(
    value: datetime | None,
    style: str = "default",
    language: str | None = None,
) -> str:
    """Render a human-facing datetime in the active locale.

    ``short`` intentionally omits the year for compact timeline/message surfaces.
    """
    if value is None or not isinstance(value, datetime):
        return ""

    code = normalized_language_code(language)
    display_value = _presentation_datetime(value)
    time_text = localized_time(display_value, code)

    if style == "short":
        if code == "fa":
            _, jm, jd = _gregorian_to_jalali(display_value.date())
            date_text = _localized_digits(f"{jd} {_PERSIAN_MONTHS[jm]}", code)
            return f"{date_text}، {time_text}"
        if code == "tr":
            date_text = _localized_django_date(display_value, "j M", code)
            return f"{date_text}, {time_text}"
        if code == "ar":
            date_text = _localized_digits(_localized_django_date(display_value, "j F", code), code)
            return f"{date_text}، {time_text}"
        date_text = _localized_django_date(display_value, "M j", code)
        return f"{date_text}, {time_text}"

    date_text = localized_date(display_value, code)
    separator = "، " if code in {"fa", "ar"} else ", "
    return f"{date_text}{separator}{time_text}"
