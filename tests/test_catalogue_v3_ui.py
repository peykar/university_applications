from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[1]


class CatalogueV3UIContractTests(SimpleTestCase):
    def test_public_and_customer_templates_do_not_read_legacy_offering_fields(self):
        paths = [
            ROOT / "templates/public/program_detail.html",
            ROOT / "templates/public/program_list.html",
            ROOT / "templates/public/university_detail.html",
            ROOT / "templates/leads/lead_section.html",
            ROOT / "templates/leads/lead_detail.html",
            ROOT / "templates/applications/customer_detail.html",
            ROOT / "templates/agents/student_detail.html",
        ]
        legacy_tokens = (
            ".semester",
            ".tuition_discounted",
            ".tuition_cash",
            ".preparatory_tuition",
        )
        for path in paths:
            source = path.read_text()
            for token in legacy_tokens:
                self.assertNotIn(token, source, f"{path} still uses Catalogue v2 token {token}")

    def test_program_filters_use_canonical_intake_parameter(self):
        source = (ROOT / "apps/public/services/program_filters.py").read_text()
        self.assertIn('intake: str = ""', source)
        self.assertIn('params.get("intake")', source)
        self.assertIn("offerings.filter(intake_id=intake_id)", source)
        self.assertNotIn('params.get("semester")', source)

    def test_public_program_detail_uses_structured_fees(self):
        source = (ROOT / "templates/public/program_detail.html").read_text()
        self.assertIn("offering.display_tuition_fee", source)
        self.assertIn("offering.display_fees", source)
        self.assertIn("offering.intake.name_en", source)
