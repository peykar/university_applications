import json

from django import template

register = template.Library()


@register.filter
def json_ld(value) -> str:
    """Serialize trusted schema data safely for an application/ld+json script."""
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return serialized.replace("</", "<\\/")
