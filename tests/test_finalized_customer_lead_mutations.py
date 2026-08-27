from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FinalizedCustomerLeadMutationStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/leads/views.py").read_text(encoding="utf-8")
        self.header = (root / "templates" / "includes" / "applicant_entity_header.html").read_text(
            encoding="utf-8"
        )
        self.detail = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        )
        self.section = (root / "templates" / "leads" / "lead_section.html").read_text(
            encoding="utf-8"
        )

    def test_customer_profile_edit_has_finalized_guard(self):
        edit_block = self.views.split("def lead_edit", 1)[1].split(
            "def lead_preferences",
            1,
        )[0]
        self.assertIn("lead.status == LeadStatus.FINALIZED", edit_block)
        self.assertIn(
            'if lead.status != "finalized"',
            self.header,
        )

    def test_customer_document_mutations_have_finalized_guards(self):
        upload_block = self.views.split("def lead_document_upload", 1)[1].split(
            "def lead_document_replace",
            1,
        )[0]
        replace_block = self.views.split("def lead_document_replace", 1)[1].split(
            "def lead_send_message",
            1,
        )[0]
        self.assertIn("lead.status == LeadStatus.FINALIZED", upload_block)
        self.assertIn("lead.status == LeadStatus.FINALIZED", replace_block)

    def test_finalized_document_ui_is_read_only(self):
        self.assertIn(
            'document.review_status == "replacement_requested" and lead.status != "finalized"',
            self.detail,
        )
        self.assertIn(
            'if lead.status != "finalized"',
            self.detail,
        )
        self.assertIn(
            'if lead.status != "finalized"',
            self.section,
        )
        self.assertIn("Applicant documents are read-only", self.detail)
        self.assertIn("Applicant documents are read-only", self.section)
