from pathlib import Path

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve
from django.utils.translation import override

from apps.public.context_processors import seo


@override_settings(SITE_URL="https://turkdemy.com")
class PublicSEOTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        root = Path(settings.BASE_DIR)
        self.base_template = (root / "templates" / "base.html").read_text(encoding="utf-8")
        self.agent_contract = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.root_urls = (root / "turkdemy" / "urls.py").read_text(encoding="utf-8")

    def _request(self, path: str):
        request = self.factory.get(path)
        request.resolver_match = resolve(path)
        return request

    def test_public_page_contract_requires_seo_review(self):
        self.assertIn("## Public-page SEO gate", self.agent_contract)
        self.assertIn(
            "Every change that adds or modifies a public page MUST include an SEO",
            self.agent_contract,
        )

    def test_public_home_has_canonical_and_language_alternates(self):
        with override("en"):
            context = seo(self._request("/en/"))

        self.assertEqual(context["seo_canonical_url"], "https://turkdemy.com/en/")
        alternates = {item["language"]: item["href"] for item in context["seo_alternates"]}
        self.assertEqual(alternates["en"], "https://turkdemy.com/en/")
        self.assertEqual(alternates["fa"], "https://turkdemy.com/fa/")
        self.assertEqual(alternates["tr"], "https://turkdemy.com/tr/")
        self.assertEqual(alternates["ar"], "https://turkdemy.com/ar/")
        self.assertEqual(alternates["x-default"], "https://turkdemy.com/en/")

    def test_filtered_catalogue_is_noindex(self):
        request = self.factory.get("/en/programs/?degree=bachelor")
        request.resolver_match = resolve("/en/programs/")
        with override("en"):
            context = seo(request)
        self.assertEqual(context["seo_robots"], "noindex,follow")
        self.assertEqual(
            context["seo_canonical_url"],
            "https://turkdemy.com/en/programs/",
        )

    def test_pagination_self_canonicalizes(self):
        request = self.factory.get("/en/programs/?page=2")
        request.resolver_match = resolve("/en/programs/")
        with override("en"):
            context = seo(request)
        self.assertEqual(context["seo_robots"], "index,follow")
        self.assertEqual(
            context["seo_canonical_url"],
            "https://turkdemy.com/en/programs/?page=2",
        )

    def test_general_field_landing_route_is_indexable_and_localized(self):
        request = self._request("/en/programs/fields/engineering/")
        with override("en"):
            context = seo(request)
        self.assertEqual(context["seo_robots"], "index,follow")
        self.assertEqual(
            context["seo_canonical_url"],
            "https://turkdemy.com/en/programs/fields/engineering/",
        )
        alternates = {item["language"]: item["href"] for item in context["seo_alternates"]}
        self.assertEqual(
            alternates["fa"],
            "https://turkdemy.com/fa/programs/fields/engineering/",
        )

    def test_shared_head_renders_required_seo_hooks(self):
        self.assertIn('rel="canonical"', self.base_template)
        self.assertIn('rel="alternate" hreflang=', self.base_template)
        self.assertIn('name="robots"', self.base_template)
        self.assertIn('property="og:url"', self.base_template)
        self.assertIn('name="twitter:card"', self.base_template)

    def test_root_robots_and_sitemap_routes_are_registered(self):
        self.assertIn('path("robots.txt", robots_txt', self.root_urls)
        self.assertIn('path("sitemap.xml", sitemap_xml', self.root_urls)
