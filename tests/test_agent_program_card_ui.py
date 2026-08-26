from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramCardUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_suggest_action_is_compact_and_explicit(self):
        self.assertIn("program-suggest-action", self.template)
        self.assertIn('aria-hidden="true">+</span>', self.template)
        self.assertIn("min-height:28px", self.css)

    def test_program_rows_have_polished_layout_hook(self):
        self.assertIn("agent-list-row program-interest-row", self.template)
        self.assertIn(".program-interest-row+", self.css)

    def test_program_source_badges_can_be_visually_distinguished(self):
        self.assertIn("program-source-{{ interest.source }}", self.template)
        self.assertIn(".program-source-agent", self.css)
        self.assertIn(".program-source-user", self.css)
