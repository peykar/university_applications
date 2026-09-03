from django import template

from apps.core.localization import (
    localized_date,
    localized_datetime,
    localized_time,
    localized_value,
)

register = template.Library()


@register.filter(name="localized")
def localized_filter(value, field="name"):
    """Render a localized structured value with canonical-English fallback."""
    return localized_value(value, field)


@register.filter(name="localized_date")
def localized_date_filter(value):
    """Render a display date using the active locale/calendar."""
    return localized_date(value)


@register.filter(name="localized_datetime")
def localized_datetime_filter(value, style="default"):
    """Render a display datetime using the active locale/calendar."""
    return localized_datetime(value, style=style)


@register.filter(name="localized_time")
def localized_time_filter(value):
    """Render a display time using locale-appropriate numerals."""
    return localized_time(value)
