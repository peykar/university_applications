from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class StudentApplicationWorkflowTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.service = (root / "apps/applications/services.py").read_text(encoding="utf-8")
        self.student_template = (root / "templates/agents/student_detail.html").read_text(
            encoding="utf-8"
        )
        self.applicant_template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_student_has_agent_workspace(self):
        self.assertIn("def student_detail", self.views)
        self.assertIn('name="agent-student-detail"', self.urls)
        self.assertIn("Programs discussed during applicant stage", self.student_template)

    def test_discussed_program_can_start_application(self):
        self.assertIn(
            "def student_start_discussed_application",
            self.views,
        )
        self.assertIn("Start application", self.student_template)

    def test_new_application_can_be_created_directly(self):
        self.assertIn("def student_new_application", self.views)
        self.assertIn("New application", self.student_template)
        self.assertIn("StudentApplicationOfferingForm", self.views)

    def test_application_service_requires_concrete_offering_and_prevents_duplicates(self):
        self.assertIn("program_offering=offering", self.service)
        self.assertIn("status=ApplicationStatus.DRAFT", self.service)
        self.assertIn("active application for this student and intake", self.service)
        self.assertIn("tuition=offering.tuition", self.service)
        self.assertIn("deposit=offering.deposit", self.service)

    def test_application_service_does_not_persist_lead_interest_link(self):
        self.assertNotIn("source_interest", self.service)
        models_source = (Path(settings.BASE_DIR) / "apps/leads/models.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("converted_application = models.OneToOneField", models_source)

    def test_finalized_lead_links_to_agent_student_workspace(self):
        self.assertIn("agent-student-detail", self.applicant_template)
        self.assertNotIn("admin:students_student_change", self.applicant_template)

    def test_offering_form_narrows_model_choice_field_safely(self):
        forms_source = (Path(settings.BASE_DIR) / "apps/agents/forms.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "isinstance(offering_field, forms.ModelChoiceField)",
            forms_source,
        )
        self.assertIn("offering_field.queryset =", forms_source)

    def test_offering_queryset_uses_translated_name_fields(self):
        forms_source = (Path(settings.BASE_DIR) / "apps/agents/forms.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"academic_year__name_en"', forms_source)
        self.assertIn('"semester__name_en"', forms_source)
        self.assertNotIn('"academic_year__name"', forms_source)
        self.assertNotIn('"semester__name"', forms_source)
