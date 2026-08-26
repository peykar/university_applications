from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramSuggestionCompactUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")
        self.js = (root / "static/js/searchable_program_suggestion.js").read_text(encoding="utf-8")

    def test_modal_uses_compact_variant(self):
        self.assertIn("compact-program-modal", self.template)
        self.assertIn("compact-program-form", self.template)
        self.assertIn("compact-modal-actions", self.template)

    def test_search_controls_are_compact(self):
        self.assertIn("compact-search-input", self.js)
        self.assertIn("min-height:36px", self.css)
        self.assertIn("max-width:560px", self.css)

    def test_results_dropdown_is_compact(self):
        self.assertIn("compact-picker-options", self.js)
        self.assertIn("max-height:210px", self.css)
