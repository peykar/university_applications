from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MobilePublicShellTests(SimpleTestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.base_template = (base / "templates" / "base.html").read_text(encoding="utf-8")
        self.program_template = (base / "templates" / "public" / "program_list.html").read_text(
            encoding="utf-8"
        )
        self.css = (base / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

    def test_global_mobile_navigation_exists(self):
        self.assertIn("mobile-nav-toggle", self.base_template)
        self.assertIn('id="mobile-site-menu"', self.base_template)

    def test_program_title_does_not_contain_script(self):
        title_start = self.program_template.index("{% block title %}")
        title_end = self.program_template.index("{% endblock %}", title_start)
        self.assertNotIn("<script", self.program_template[title_start:title_end])

    def test_mobile_content_uses_viewport_width(self):
        self.assertIn(".page-shell{", self.css)
        self.assertIn("width:calc(100% - 22px)!important;", self.css)
        self.assertIn("@media(max-width:360px)", self.css)
