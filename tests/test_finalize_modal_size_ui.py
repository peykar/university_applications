from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FinalizeModalSizeUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_finalize_modal_has_dedicated_size_hook(self):
        self.assertIn(
            'class="agent-modal finalize-applicant-modal"',
            self.template,
        )
        self.assertIn("max-width:980px", self.css)

    def test_finalize_controls_are_more_readable(self):
        self.assertIn("minmax(280px,360px)", self.css)
        self.assertIn("min-height:36px", self.css)
        self.assertIn("font-size:1rem", self.css)
        self.assertIn("min-height:42px", self.css)

    def test_finalize_modal_remains_responsive(self):
        self.assertIn("@media(max-width:760px)", self.css)
        self.assertIn("width:calc(100vw - 20px)", self.css)
