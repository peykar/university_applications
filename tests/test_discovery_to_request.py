from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class DiscoveryToRequestContractTests(SimpleTestCase):
    def test_program_detail_links_canonical_city_and_field_routes(self):
        template = (ROOT / "templates/public/program_detail.html").read_text()

        self.assertIn(
            "{% url 'university-city-detail' program.university.city.slug_en %}",
            template,
        )
        self.assertIn("{% url 'program-field-detail' field.slug_en %}", template)
        self.assertIn("program.general_fields.all", template)
        self.assertNotIn("?city={{ program.university.city.slug_en }}", template)
        self.assertNotIn("?field={{ field.slug_en }}", template)

    def test_program_detail_prefetches_general_fields(self):
        view_source = (ROOT / "apps/public/views.py").read_text()
        detail_source = view_source.split("def program_detail(request, slug):", 1)[1].split(
            "\ndef faq(request):", 1
        )[0]

        self.assertIn('"general_fields",', detail_source)

    def test_program_conversion_uses_request_terminology(self):
        detail = (ROOT / "templates/public/program_detail.html").read_text()
        apply_page = (ROOT / "templates/leads/apply_program.html").read_text()

        self.assertIn('{% trans "Start a Request" %}', detail)
        self.assertIn('{% trans "Start a Request" %}', apply_page)
        self.assertIn('{% trans "Who is this Request for?" %}', apply_page)
        self.assertIn('{% trans "Continue Request" %}', apply_page)
        self.assertNotIn("Apply / I'm interested", detail)
        self.assertNotIn("Apply / express interest", apply_page)
        self.assertNotIn("Continue application", apply_page)
