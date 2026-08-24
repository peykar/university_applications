from __future__ import annotations

from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from django.utils.translation import override


def absolute_url(
    viewname: str,
    *args,
    language: str | None = None,
    **kwargs,
) -> str:
    """
    Build a canonical absolute URL using settings.SITE_URL.

    Use this for emails, notifications, background tasks, exports, and other
    contexts where no HTTP request is available.
    """
    if language:
        with override(language):
            path = reverse(viewname, args=args, kwargs=kwargs)
    else:
        path = reverse(viewname, args=args, kwargs=kwargs)

    return urljoin(f"{settings.SITE_URL}/", path.lstrip("/"))


def absolute_path(path: str) -> str:
    """
    Convert a relative application path to an absolute canonical URL.
    """
    return urljoin(f"{settings.SITE_URL}/", path.lstrip("/"))
