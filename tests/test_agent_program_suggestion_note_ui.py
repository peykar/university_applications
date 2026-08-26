from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentProgramSuggestionNoteUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.forms = (root / "apps/agents/forms.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_note_label_is_optional_and_compact(self):
        self.assertIn("Suggestion note (optional)", self.forms)
        self.assertIn('"rows": 2', self.forms)
        self.assertIn("compact-note-input", self.forms)

    def test_note_has_light_helper_text(self):
        self.assertIn("Add a short reason only if it helps", self.template)
        self.assertIn("compact-note-field", self.template)

    def test_note_textarea_is_shorter(self):
        self.assertIn("min-height:52px", self.css)
        self.assertIn("height:52px", self.css)
