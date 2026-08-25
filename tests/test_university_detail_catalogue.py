from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class UniversityDetailCatalogueTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.detail = (base / "templates" / "public" / "university_detail.html").read_text(
            encoding="utf-8"
        )
        self.program_list = (base / "templates" / "public" / "program_list.html").read_text(
            encoding="utf-8"
        )

    def test_both_pages_reuse_program_card(self):
        include = "public/includes/program_discovery_card.html"
        self.assertIn(include, self.detail)
        self.assertIn(include, self.program_list)

    def test_detail_uses_catalogue_layout(self):
        self.assertIn("programs-catalogue-shell", self.detail)
        self.assertIn("programs-filter-panel", self.detail)
        self.assertIn("programs-results-panel", self.detail)

    def test_detail_supports_filter_chips_and_mobile_drawer(self):
        self.assertIn("active-filter-chip", self.detail)
        self.assertIn("mobile-filter-trigger", self.detail)
        self.assertIn("filters-modal-open", self.detail)
