from __future__ import annotations

from html import escape
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import override

from apps.universities.models import Program, University


def _absolute(path: str) -> str:
    return urljoin(f"{settings.SITE_URL.rstrip('/')}/", path.lstrip("/"))


def _localized_url(viewname: str, language: str, **kwargs) -> str:
    with override(language):
        return _absolute(reverse(viewname, kwargs=kwargs or None))


def robots_txt(_request):
    sitemap = _absolute("/sitemap.xml")
    body = f"User-agent: *\nAllow: /\nSitemap: {sitemap}\n"
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


def sitemap_xml(_request):
    static_routes = ("home", "university-list", "program-list", "faq", "about", "contact")
    entries: list[tuple[str, dict[str, str]]] = []

    for viewname in static_routes:
        alternates = {code: _localized_url(viewname, code) for code, _name in settings.LANGUAGES}
        entries.append((alternates.get("en") or next(iter(alternates.values())), alternates))

    for university in University.objects.filter(is_active=True).exclude(slug_en=""):
        alternates = {
            code: _localized_url(
                "university-detail",
                code,
                slug=university.slug_en,
            )
            for code, _name in settings.LANGUAGES
        }
        entries.append((alternates.get("en") or next(iter(alternates.values())), alternates))

    for program in (
        Program.objects.filter(is_active=True, university__is_active=True)
        .exclude(slug_en="")
        .only("slug_en")
    ):
        alternates = {
            code: _localized_url("program-detail", code, slug=program.slug_en)
            for code, _name in settings.LANGUAGES
        }
        entries.append((alternates.get("en") or next(iter(alternates.values())), alternates))

    rows = []
    for location, alternates in entries:
        alternate_template = '<xhtml:link rel="alternate" hreflang="{lang}" href="{href}" />'
        alternate_links = "".join(
            alternate_template.format(
                lang=escape(language, quote=True),
                href=escape(href, quote=True),
            )
            for language, href in alternates.items()
        )
        x_default = alternates.get("en")
        if x_default:
            alternate_links += (
                '<xhtml:link rel="alternate" hreflang="x-default" href="'
                f'{escape(x_default, quote=True)}" />'
            )
        rows.append(f"<url><loc>{escape(location)}</loc>{alternate_links}</url>")

    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(rows) + "</urlset>"
    )
    return HttpResponse(body, content_type="application/xml; charset=utf-8")
