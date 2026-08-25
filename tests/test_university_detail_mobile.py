from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class UniversityDetailMobileTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.detail = (base / "templates" / "public" / "university_detail.html").read_text(
            encoding="utf-8"
        )
        self.card = (
            base / "templates" / "public" / "includes" / "program_discovery_card.html"
        ).read_text(encoding="utf-8")
        self.css = (base / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

    def test_university_cards_hide_redundant_brand(self):
        self.assertIn("hide_university_brand=True", self.detail)
        self.assertIn("{% if not hide_university_brand %}", self.card)

    def test_mobile_catalogue_has_compact_result_summary(self):
        self.assertIn("university-mobile-catalogue-summary", self.detail)

    def test_closed_mobile_filter_does_not_take_space(self):
        self.assertIn(
            ".university-programs-shell>.programs-filter-panel{",
            self.css,
        )
        self.assertIn(
            ".university-programs-shell>.programs-filter-panel.mobile-filters-open{",
            self.css,
        )

    def test_mobile_banner_gets_real_visual_height(self):
        self.assertIn("min-height:185px;", self.css)
