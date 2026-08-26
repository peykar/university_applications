from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ApplicationStatusUITests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        )
        self.views = (root / "apps" / "leads" / "views.py").read_text(encoding="utf-8")
        self.models = (root / "apps" / "leads" / "models.py").read_text(encoding="utf-8")

    def test_apply_flow_uses_explicit_applied_state(self):
        self.assertIn('APPLIED = "applied"', self.models)
        self.assertIn("LeadProgramInterestStatus.APPLIED", self.views)

    def test_customer_sees_applications_and_intake(self):
        self.assertIn("Applications & program interests", self.template)
        self.assertIn('interest.status == "applied"', self.template)
        self.assertIn("Any intake / decide later", self.template)

    def test_success_message_is_application_specific(self):
        self.assertIn("Application started for", self.views)
