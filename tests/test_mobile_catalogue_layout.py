from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MobileCatalogueLayoutTests(SimpleTestCase):
    def setUp(self):
        self.css = (Path(settings.BASE_DIR) / "static" / "css" / "turkdemy.css").read_text(
            encoding="utf-8"
        )

    def test_closed_mobile_filter_is_removed_from_flow(self):
        self.assertIn(".programs-filter-panel{", self.css)
        self.assertIn("display:none!important;", self.css)
        self.assertIn(
            ".programs-filter-panel.mobile-filters-open{",
            self.css,
        )
        self.assertIn("display:block!important;", self.css)

    def test_program_results_are_single_column_on_mobile(self):
        self.assertIn(".programs-result-grid{", self.css)
        self.assertIn(
            "grid-template-columns:minmax(0,1fr)!important;",
            self.css,
        )

    def test_shared_public_grids_are_mobile_safe(self):
        for selector in (
            ".card-grid",
            ".university-grid",
            ".program-result-grid",
            ".related-program-grid",
            ".offering-card-grid",
        ):
            self.assertIn(selector, self.css)
