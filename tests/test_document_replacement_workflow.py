from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class DocumentReplacementWorkflowStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.models = (root / "apps" / "leads" / "models.py").read_text(encoding="utf-8")
        self.lead_views = (root / "apps" / "leads" / "views.py").read_text(encoding="utf-8")
        self.agent_views = (root / "apps" / "agents" / "views.py").read_text(encoding="utf-8")
        self.customer_template = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        ) + (root / "templates" / "leads" / "lead_section.html").read_text(encoding="utf-8")

    def test_rejected_is_replacement_requested(self):
        review_status_block = self.models.split(
            "class LeadDocumentReviewStatus(models.TextChoices):",
            1,
        )[1].split("class LeadDocument(BaseModel):", 1)[0]
        self.assertIn(
            'REPLACEMENT_REQUESTED = "replacement_requested"',
            review_status_block,
        )
        self.assertNotIn(
            'REJECTED = "rejected"',
            review_status_block,
        )

    def test_agent_request_creates_history_and_message(self):
        self.assertIn("LeadDocumentReviewHistory.objects.create(", self.agent_views)
        self.assertIn(
            "event_type=SystemMessageEventType.DOCUMENT_REPLACEMENT_REQUESTED",
            self.agent_views,
        )
        self.assertIn('"document_type": document.document_type', self.agent_views)
        self.assertIn('"reason": reason', self.agent_views)

    def test_customer_can_replace_requested_document(self):
        self.assertIn("def lead_document_replace", self.lead_views)
        self.assertIn("LeadDocumentVersion(", self.lead_views)
        self.assertIn("Needs replacement", self.customer_template)
        self.assertIn("Replace document", self.customer_template)

    def test_replacement_resets_review(self):
        self.assertIn("LeadDocumentReviewStatus.PENDING", self.lead_views)
        self.assertIn('document.review_note = ""', self.lead_views)
        self.assertIn("document.reviewed_by = None", self.lead_views)
