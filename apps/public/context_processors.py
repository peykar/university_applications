from __future__ import annotations

from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import get_language, override

_INDEXABLE_PUBLIC_ROUTES = {
    "home",
    "university-list",
    "university-detail",
    "university-city-detail",
    "program-list",
    "program-field-detail",
    "program-detail",
    "faq",
    "about",
    "contact",
}


def _absolute(path: str) -> str:
    return urljoin(f"{settings.SITE_URL.rstrip('/')}/", path.lstrip("/"))


def _route_url(request, language: str) -> str | None:
    match = request.resolver_match
    if match is None or match.url_name not in _INDEXABLE_PUBLIC_ROUTES:
        return None
    try:
        with override(language):
            path = reverse(match.url_name, kwargs=match.kwargs)
    except NoReverseMatch:
        return None

    # Pagination represents a distinct catalogue page. Other public filters/search
    # are useful navigation but are not standalone SEO landing pages.
    page = (request.GET.get("page") or "").strip()
    if page and page.isdigit() and int(page) > 1:
        path = f"{path}?{urlencode({'page': page})}"
    return _absolute(path)


def seo(request):
    """Shared technical-SEO context for public and non-public templates."""
    language = (get_language() or settings.LANGUAGE_CODE).split("-", 1)[0]
    canonical = _route_url(request, language)
    is_public_indexable_route = (
        request.resolver_match is not None
        and request.resolver_match.url_name in _INDEXABLE_PUBLIC_ROUTES
    )
    non_page_query = any(key != "page" for key in request.GET)
    robots = (
        "index,follow" if is_public_indexable_route and not non_page_query else "noindex,follow"
    )

    alternates: list[dict[str, str]] = []
    if canonical:
        for code, _name in settings.LANGUAGES:
            href = _route_url(request, code)
            if href:
                alternates.append({"language": code, "href": href})
        with override("en"):
            x_default = _route_url(request, "en")
        if x_default:
            alternates.append({"language": "x-default", "href": x_default})

    return {
        "seo_canonical_url": canonical,
        "seo_alternates": alternates,
        "seo_robots": robots,
    }
