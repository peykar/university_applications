from __future__ import annotations

from urllib.parse import urljoin

from django.conf import settings
from django.urls import path, reverse
from django.utils.translation import override

from . import views


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
            relative_path = reverse(viewname, args=args, kwargs=kwargs)
    else:
        relative_path = reverse(viewname, args=args, kwargs=kwargs)

    return urljoin(
        f"{settings.SITE_URL}/",
        relative_path.lstrip("/"),
    )


def absolute_path(path: str) -> str:
    """
    Convert a relative application path to an absolute canonical URL.
    """
    return urljoin(f"{settings.SITE_URL}/", path.lstrip("/"))


urlpatterns = [
    path(
        "email-previews/",
        views.email_preview_gallery,
        name="email-preview-gallery",
    ),
    path(
        "email-previews/<str:email_type>/<str:language>/html/",
        views.email_preview_html,
        name="email-preview-html",
    ),
    path(
        "email-previews/<str:email_type>/<str:language>/",
        views.email_preview_detail,
        name="email-preview-detail",
    ),
    path(
        "email-previews/<str:email_type>/<str:language>/send/",
        views.send_email_preview,
        name="email-preview-send",
    ),
]
