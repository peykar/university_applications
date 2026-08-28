from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class StudentRecordConversionStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.forms = (root / "apps/agents/forms.py").read_text(encoding="utf-8")
        self.conversion = (root / "apps/leads/services/conversion.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/student_record_create.html").read_text(
            encoding="utf-8"
        )

    def test_conversion_is_a_full_page_workflow(self):
        self.assertIn("class StudentRecordConversionForm", self.forms)
        self.assertIn('"agents/student_record_create.html"', self.views)
        self.assertIn("Create Student Record", self.template)
        self.assertNotIn("finalize-applicant-modal", self.template)

    def test_document_selection_is_explicit(self):
        self.assertIn('name="document"', self.template)
        self.assertIn("if document.is_verified", self.views)
        self.assertIn("_copy_selected_documents", self.conversion)
        self.assertIn("Approved during Student record creation.", self.conversion)

    def test_program_selection_is_optional_but_offering_required_when_selected(self):
        self.assertIn('request.POST.getlist("program_interest")', self.views)
        self.assertIn("Choose an offering for", self.views)
        self.assertIn("Select zero or more discussed programs", self.template)

    def test_conversion_does_not_link_interest_to_application(self):
        self.assertNotIn("converted_application", self.conversion)
        self.assertNotIn("source_interest=", self.conversion)
