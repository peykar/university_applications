from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ApplyProgramDirectIntakeStructureTests(SimpleTestCase):
    def test_first_time_user_can_create_applicant_inline(self):
        source = (Path(settings.BASE_DIR) / "apps" / "leads" / "views.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('applicant_choice == "self_new"', source)
        self.assertIn("Lead.objects.create(", source)
        self.assertNotIn(
            "if not Lead.objects.filter(user=request.user).exists():",
            source,
        )

    def test_applicant_form_explains_optional_intake(self):
        template = (Path(settings.BASE_DIR) / "templates" / "leads" / "lead_form.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("Most fields are optional", template)
        self.assertIn("Who are you applying for?", template)
        self.assertIn("form.applicant_for", template)
