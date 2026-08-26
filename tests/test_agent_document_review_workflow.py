from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentDocumentReviewWorkflowStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.models = (root / "apps" / "leads" / "models.py").read_text(encoding="utf-8")
        self.views = (root / "apps" / "agents" / "views.py").read_text(encoding="utf-8")
        self.template = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_document_has_review_workflow_fields(self):
        self.assertIn("class LeadDocumentReviewStatus", self.models)
        self.assertIn("review_status = models.CharField", self.models)
        self.assertIn("reviewed_by = models.ForeignKey", self.models)
        self.assertIn("review_note = models.TextField", self.models)

    def test_chat_attachment_can_be_promoted_to_document(self):
        self.assertIn("applicant_attachment_to_document", self.views)
        self.assertIn("source_message_attachment=attachment", self.views)
        self.assertIn("Add to documents", self.template)

    def test_agent_can_open_and_review_document(self):
        self.assertIn("applicant_document_review", self.views)
        self.assertIn("Save review", self.template)
        self.assertIn("Request replacement", self.template)
        self.assertIn('class="agent-modal"', self.template)
        self.assertIn('data-modal-target="document-review-', self.template)

    def test_agent_program_panel_no_longer_reads_removed_interest_status(self):
        self.assertNotIn("interest.get_status_display", self.template)
        self.assertIn("Agent-suggested", self.template)
        self.assertIn("User-added", self.template)

    def test_chat_promotion_uses_modal_instead_of_inline_form(self):
        self.assertIn('data-modal-target="promote-attachment-', self.template)
        self.assertIn("Conversation attachment", self.template)
        self.assertNotIn('<details class="attachment-promote">', self.template)

    def test_approved_document_does_not_show_review_action(self):
        self.assertIn(
            '{% if document.review_status != "approved" %}',
            self.template,
        )

    def test_document_type_is_the_open_link(self):
        self.assertIn('class="document-type-link"', self.template)
        self.assertIn('href="{{ document.file.url }}"', self.template)
        self.assertIn('title="{{ document.name }}"', self.template)
        self.assertNotIn('class="document-file-link"', self.template)
