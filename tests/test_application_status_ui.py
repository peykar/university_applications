from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ApplicantProgramSourceUITests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        ) + (root / "templates" / "leads" / "lead_section.html").read_text(encoding="utf-8")
        self.models = (root / "apps" / "leads" / "models.py").read_text(encoding="utf-8")

    def test_only_user_and_agent_program_sources_exist(self):
        source_block = self.models.split(
            "class LeadProgramInterestSource(models.TextChoices):",
            1,
        )[1].split("class LeadProgramInterest(BaseModel):", 1)[0]
        self.assertIn('USER = "user"', source_block)
        self.assertIn('AGENT = "agent"', source_block)
        self.assertNotIn('SYSTEM = "system"', source_block)

    def test_customer_program_ui_uses_source_not_interest_status(self):
        program_section = self.template.split(
            '<div class="lead-interest-list request-program-list">',
            1,
        )[1].split("</section>", 1)[0]
        self.assertIn("Suggested by your advisor", program_section)
        self.assertIn("Added by you", program_section)
        self.assertNotIn("get_status_display", program_section)

    def test_program_section_is_simple(self):
        self.assertIn('{% trans "Programs" %}', self.template)
        self.assertIn("Intake to be decided", self.template)
