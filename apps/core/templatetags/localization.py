from django import template

from apps.core.localization import localized_value

register = template.Library()


@register.filter(name="localized")
def localized_filter(value, field="name"):
    """Render a localized structured value with canonical-English fallback."""
    return localized_value(value, field)
