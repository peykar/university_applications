from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class CustomerDocumentUploadModalTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.form_source = (root / "apps" / "leads" / "forms.py").read_text(encoding="utf-8")
        self.template = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        )

    def test_customer_upload_form_does_not_ask_for_document_name(self):
        form_block = self.form_source.split(
            "class LeadDocumentForm(forms.ModelForm):",
            1,
        )[1].split("class LeadDocumentReplacementForm", 1)[0]
        self.assertIn(
            'fields = ("document_type", "file", "description")',
            form_block,
        )
        self.assertNotIn('"name"', form_block)

    def test_document_upload_uses_modal(self):
        self.assertIn('id="customer-document-upload"', self.template)
        self.assertIn('data-modal-target="customer-document-upload"', self.template)
        self.assertNotIn('<details class="lead-upload-panel">', self.template)

    def test_modal_explains_name_is_automatic(self):
        self.assertIn(
            "The filename is kept automatically",
            self.template,
        )

    def test_modal_trigger_script_is_rendered_in_content(self):
        title_block = self.template.split("{% block title %}", 1)[1].split(
            "{% endblock %}",
            1,
        )[0]
        self.assertNotIn("modal-trigger", title_block)
        self.assertIn(
            "document.getElementById(trigger.dataset.modalTarget)",
            self.template,
        )
        self.assertIn("dialog.showModal()", self.template)
