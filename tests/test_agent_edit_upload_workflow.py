from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentEditUploadWorkflowTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.forms = (root / "apps/agents/forms.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.template = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_agent_can_edit_provisional_lead_data(self):
        self.assertIn("class AgentLeadEditForm", self.forms)
        self.assertIn("def applicant_edit", self.views)
        self.assertIn('name="agent-applicant-edit"', self.urls)
        self.assertIn("Edit applicant", self.template)

    def test_agent_can_upload_external_document(self):
        self.assertIn("class AgentLeadDocumentUploadForm", self.forms)
        self.assertIn("def applicant_document_upload", self.views)
        self.assertIn('name="agent-applicant-document-upload"', self.urls)
        self.assertIn('enctype="multipart/form-data"', self.template)

    def test_uploaded_document_has_agent_audit_activity(self):
        self.assertIn("LeadActivityType.DOCUMENT_UPLOADED", self.views)
        self.assertIn("uploaded by agent user", self.views)

    def test_finalized_lead_is_not_edited_as_lead(self):
        self.assertIn("Finalized or closed applicant data cannot be edited here.", self.views)
        self.assertIn("Upload documents to the Student record after finalization.", self.views)

    def test_form_errors_are_coerced_to_strings(self):
        self.assertIn("str(message)", self.views)
        self.assertIn("for field_messages in form.errors.values()", self.views)
        self.assertIn("for message in field_messages", self.views)
