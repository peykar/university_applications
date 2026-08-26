from pathlib import Path

from django.test import SimpleTestCase


class ApplicantDetailDesignTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.template = (root / "templates/leads/lead_detail.html").read_text()
        self.css = (root / "static/css/turkdemy.css").read_text()

    def test_customer_workspace_has_scoped_design_wrapper(self):
        self.assertIn('class="customer-applicant-page"', self.template)
        self.assertIn(".customer-applicant-page .applicant-workspace", self.css)

    def test_document_upload_uses_styled_form(self):
        self.assertIn("document-upload-form", self.template)
        self.assertIn(
            ".customer-applicant-page .document-upload-form",
            self.css,
        )

    def test_chat_composer_has_responsive_file_control(self):
        self.assertIn('class="chat-file-control"', self.template)
        self.assertIn(
            ".customer-applicant-page .chat-file-control",
            self.css,
        )

    def test_mobile_layout_stacks_sidebar_and_forms(self):
        self.assertIn("@media(max-width:700px)", self.css)
        self.assertIn(
            ".customer-applicant-page .applicant-sidebar{grid-template-columns:1fr}",
            self.css,
        )
