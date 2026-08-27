from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class StudentApplicationDocumentWorkflowTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.student = (root / "templates/agents/student_detail.html").read_text(encoding="utf-8")
        self.application = (root / "templates/agents/application_detail.html").read_text(
            encoding="utf-8"
        )

    def test_agent_can_upload_student_document(self):
        self.assertIn("def student_document_upload", self.views)
        self.assertIn("request.FILES", self.views)
        self.assertIn("agent-student-document-upload", self.urls)
        self.assertIn("Upload document", self.student)

    def test_application_can_reuse_student_document(self):
        self.assertIn("def application_add_existing_document", self.views)
        self.assertIn("ApplicationDocument.objects.create(", self.views)
        self.assertIn("Add existing student document", self.application)

    def test_application_upload_creates_reusable_student_document(self):
        self.assertIn("def application_upload_document", self.views)
        self.assertIn("student_document.student = application.student", self.views)
        self.assertIn("Upload new document", self.application)
        self.assertIn("reusable Student document", self.application)

    def test_application_document_type_links_to_file(self):
        self.assertIn('href="{{ document.student_document.file.url }}"', self.application)
        self.assertIn('title="{{ document.student_document.file.name }}"', self.application)
