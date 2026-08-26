from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FinalizeDraftApplicationsTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.conversion = (root / "apps/leads/services/conversion.py").read_text(encoding="utf-8")
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_finalize_accepts_selected_interests(self):
        self.assertIn("selected_interest_ids:", self.conversion)
        self.assertIn(
            'request.POST.getlist("program_interests")',
            self.views,
        )
        self.assertIn('request.POST.get(f"program_offering_{interest_id}", "")', self.views)

    def test_selected_interests_create_draft_applications(self):
        self.assertIn("Application.objects.create(", self.conversion)
        self.assertIn("status=ApplicationStatus.DRAFT", self.conversion)
        self.assertIn("tuition=offering.tuition", self.conversion)
        self.assertIn("deposit=offering.deposit", self.conversion)
        self.assertIn("interest.converted_application = application", self.conversion)

    def test_programs_are_selectable_and_intake_is_chosen_at_finalization(self):
        self.assertNotIn(
            "{% if not interest.program_offering %}disabled{% endif %}",
            self.template,
        )
        self.assertIn('name="program_offering_{{ interest.pk }}"', self.template)
        self.assertIn("Choose intake", self.template)
        self.assertIn("selected_offering_ids:", self.conversion)
        self.assertIn("ProgramOffering.objects.get(", self.conversion)

    def test_selecting_no_programs_is_allowed(self):
        self.assertIn("if not selected_interest_ids:", self.conversion)
        self.assertIn("Selecting none is allowed.", self.template)
