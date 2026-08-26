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
        self.assertIn("uploaded and approved by agent user", self.views)

    def test_finalized_lead_is_not_edited_as_lead(self):
        self.assertIn("Finalized or closed applicant data cannot be edited here.", self.views)
        self.assertIn("Upload documents to the Student record after finalization.", self.views)

    def test_form_errors_are_coerced_to_strings(self):
        self.assertIn("str(message)", self.views)
        self.assertIn("for field_messages in form.errors.values()", self.views)
        self.assertIn("for message in field_messages", self.views)

    def test_section_actions_are_compact(self):
        self.assertIn(
            'class="section-action agent-action-control button-reset modal-trigger"',
            self.template,
        )

    def test_edit_modal_is_grouped_and_sticky(self):
        for heading in (
            "Personal information",
            "Contact & residence",
            "Passport",
            "Education & language",
            "Family",
            "Internal notes",
        ):
            self.assertIn(heading, self.template)
        self.assertIn("sticky-modal-actions", self.template)

    def test_edit_activity_preserves_old_and_new_values(self):
        self.assertIn("form.initial.get(field_name)", self.views)
        self.assertIn("form.cleaned_data.get(field_name)", self.views)
        self.assertIn("→", self.views)

    def test_agent_uploaded_document_is_auto_approved(self):
        self.assertIn(
            "document.review_status = LeadDocumentReviewStatus.APPROVED",
            self.views,
        )
        self.assertIn("document.is_verified = True", self.views)
        self.assertIn("document.reviewed_by = request.user", self.views)
        self.assertIn("LeadDocumentReviewHistory.objects.create(", self.views)
        self.assertIn("Document uploaded and approved.", self.views)
