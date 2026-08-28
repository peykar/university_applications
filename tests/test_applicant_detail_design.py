from pathlib import Path

from django.test import SimpleTestCase


class ApplicantDetailDesignTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.template = (root / "templates/leads/lead_detail.html").read_text() + (
            root / "templates/leads/lead_section.html"
        ).read_text()
        self.css = (root / "static/css/turkdemy.css").read_text()

    def test_customer_workspace_has_scoped_design_wrapper(self):
        self.assertIn('class="customer-applicant-page customer-request-detail"', self.template)
        self.assertIn(".request-detail-layout", self.css)

    def test_document_upload_uses_styled_modal(self):
        self.assertIn("customer-document-upload-row", self.template)
        self.assertIn('data-modal-target="customer-document-upload"', self.template)
        self.assertIn('id="customer-document-upload"', self.template)
        self.assertIn("customer-document-modal-form", self.template)
        self.assertIn(".customer-document-modal", self.css)
        self.assertNotIn('<details class="lead-upload-panel">', self.template)

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

    def test_document_modal_script_is_not_in_title_block(self):
        title_block = self.template.split("{% block title %}", 1)[1].split(
            "{% endblock %}",
            1,
        )[0]
        self.assertNotIn("<script>", title_block)
        self.assertIn(
            'document.querySelectorAll("dialog")',
            self.template,
        )
