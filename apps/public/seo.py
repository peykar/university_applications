from __future__ import annotations

from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language, override


def absolute_media_url(path: str) -> str:
    return urljoin(f"{settings.SITE_URL.rstrip('/')}/", path.lstrip("/"))


def localized_absolute_url(viewname: str, **kwargs) -> str:
    language = (get_language() or settings.LANGUAGE_CODE).split("-", 1)[0]
    with override(language):
        path = reverse(viewname, kwargs=kwargs or None)
    return absolute_media_url(path)


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": url,
            }
            for position, (name, url) in enumerate(items, start=1)
        ],
    }


def graph_schema(*nodes: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": list(nodes),
    }
