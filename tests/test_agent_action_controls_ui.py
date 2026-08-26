from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentActionControlsUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_common_secondary_actions_have_button_styling_hook(self):
        self.assertIn(
            'agent-action-control button-reset modal-trigger" '
            'data-modal-target="edit-applicant-modal"',
            self.template,
        )
        self.assertIn(
            'agent-action-control button-reset modal-trigger" '
            'data-modal-target="upload-document-modal"',
            self.template,
        )
        self.assertIn(
            "agent-action-control\" href=\"{% url 'agent-applicant-activity' lead.pk %}",
            self.template,
        )

    def test_assignment_and_notes_actions_are_clear_controls(self):
        self.assertIn(
            "responsibility-action agent-action-control",
            self.template,
        )
        self.assertIn(
            'agent-action-control button-reset modal-trigger" '
            'data-modal-target="internal-notes-modal"',
            self.template,
        )

    def test_controls_have_visible_border_background_and_pointer(self):
        self.assertIn(".agent-action-control{", self.css)
        self.assertIn("border:1px solid #ccd8df", self.css)
        self.assertIn("background:#f8fafb", self.css)
        self.assertIn("cursor:pointer", self.css)
        self.assertIn(".agent-action-control:hover", self.css)
        self.assertIn(".agent-action-control:focus-visible", self.css)
