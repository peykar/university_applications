from __future__ import annotations

import re

from django.conf import settings


def customer_support_links(request):
    """Expose optional customer support links without reading environment in templates."""
    raw_number = getattr(settings, "WHATSAPP_NUMBER", "").strip()
    digits = re.sub(r"\D", "", raw_number)
    return {
        "customer_whatsapp_number": raw_number,
        "customer_whatsapp_url": f"https://wa.me/{digits}" if digits else "",
    }
