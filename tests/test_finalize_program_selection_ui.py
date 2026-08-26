from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FinalizeProgramSelectionUiTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.css = (root / "static/css/turkdemy.css").read_text(encoding="utf-8")

    def test_candidate_program_is_a_compact_row(self):
        self.assertIn("finalize-program-row", self.template)
        self.assertIn("finalize-program-identity", self.template)
        self.assertIn(
            "grid-template-columns:minmax(0,1fr) minmax(190px,240px)",
            self.css,
        )

    def test_intake_is_part_of_same_program_row(self):
        self.assertIn("finalize-program-intake", self.template)
        self.assertIn(
            'id="program-offering-{{ interest.pk }}"',
            self.template,
        )
        self.assertIn(
            'for="program-offering-{{ interest.pk }}"',
            self.template,
        )

    def test_checked_program_gets_visible_selection_state(self):
        self.assertIn(
            ".finalize-program-row:has(.finalize-program-choice input:checked)",
            self.css,
        )

    def test_mobile_layout_stacks_program_and_intake(self):
        self.assertIn("@media(max-width:680px)", self.css)
        self.assertIn(".finalize-program-intake{", self.css)
