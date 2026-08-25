from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class PaginationLinkTests(SimpleTestCase):
    def test_pagination_forces_current_tab(self):
        template = Path(settings.BASE_DIR) / "templates" / "public" / "includes" / "pagination.html"
        source = template.read_text(encoding="utf-8")

        self.assertNotIn('target="_blank"', source)
        self.assertNotIn("window.open(", source)
        self.assertGreaterEqual(source.count('target="_self"'), 2)
