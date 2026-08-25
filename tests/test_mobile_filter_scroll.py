from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MobileFilterScrollTests(SimpleTestCase):
    def test_mobile_filter_form_is_independently_scrollable(self):
        css = (Path(settings.BASE_DIR) / "static" / "css" / "turkdemy.css").read_text(
            encoding="utf-8"
        )

        self.assertIn("grid-template-rows:auto minmax(0,1fr)!important;", css)
        self.assertIn("overflow-y:auto!important;", css)
        self.assertIn("-webkit-overflow-scrolling:touch;", css)
        self.assertIn("touch-action:pan-y;", css)
        self.assertIn("padding-bottom:88px!important;", css)
