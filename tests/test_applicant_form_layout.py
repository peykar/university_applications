from pathlib import Path

from django.test import SimpleTestCase


class ApplicantFormLayoutTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.template = (root / "templates/leads/lead_form.html").read_text()

    def test_form_is_grouped_into_clear_sections(self):
        for heading in ("Personal information", "Residence", "Passport", "Education & language"):
            self.assertIn(heading, self.template)
        self.assertGreaterEqual(self.template.count('class="applicant-form-section"'), 4)

    def test_actions_are_after_all_form_sections(self):
        actions = self.template.index('class="form-actions applicant-form-actions"')
        recommendation = self.template.index("form.needs_program_recommendation")
        self.assertGreater(actions, recommendation)

    def test_form_no_longer_uses_unstructured_as_p_rendering(self):
        self.assertNotIn("{{ form.as_p }}", self.template)
