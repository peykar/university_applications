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
        self.edit_template = (root / "templates" / "agents" / "applicant_edit.html").read_text(
            encoding="utf-8"
        )
        self.edit_field_template = (
            root / "templates" / "agents" / "includes" / "applicant_edit_field.html"
        ).read_text(encoding="utf-8")

    def test_agent_can_edit_provisional_lead_data(self):
        self.assertIn("class AgentLeadEditForm", self.forms)
        self.assertIn("def applicant_edit", self.views)
        self.assertIn('name="agent-applicant-edit"', self.urls)
        self.assertIn("Edit applicant", self.template)
        self.assertIn('"agents/applicant_edit.html"', self.views)

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

    def test_invalid_edit_rerenders_page_with_form_errors(self):
        self.assertIn('request.POST if request.method == "POST" else None', self.views)
        self.assertIn('"form": form', self.views)
        self.assertIn("field.errors", self.edit_field_template)

    def test_edit_field_partial_loads_i18n_tag_library(self):
        self.assertIn("{% load i18n %}", self.edit_field_template)

    def test_section_actions_are_compact_and_applicant_update_is_auditable(self):
        self.assertIn(
            'class="section-action" href="{% url \'agent-applicant-edit\' lead.pk %}"',
            self.template,
        )
        self.assertIn("Last updated by", self.template)
        self.assertIn("lead.updated_by", self.template)
        self.assertIn("lead.updated_at", self.template)

    def test_edit_is_full_page_grouped_form(self):
        for heading in (
            "Personal information",
            "Contact & residence",
            "Passport",
            "Education & language",
            "Family",
        ):
            self.assertIn(heading, self.edit_template)
        self.assertNotIn("Internal notes", self.edit_template)
        self.assertIn("applicant-edit-page", self.edit_template)
        self.assertIn("applicant-edit-layout", self.edit_template)
        self.assertNotIn("edit-applicant-modal", self.template)

    def test_edit_activity_preserves_old_and_new_values(self):
        activity_service = (Path(settings.BASE_DIR) / "apps/leads/services/activity.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("form.initial.get(field_name)", activity_service)
        self.assertIn("form.cleaned_data.get(field_name)", activity_service)
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
