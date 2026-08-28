from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AdminOperationsUXTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.operations = (root / "apps" / "operations" / "admin.py").read_text()
        self.messaging = (root / "apps" / "messaging" / "admin.py").read_text()
        self.students = (root / "apps" / "students" / "admin.py").read_text()

    def test_todo_admin_is_searchable_filterable_and_has_comment_inline(self):
        self.assertIn("class TodoAdmin", self.operations)
        self.assertIn("search_fields = (", self.operations)
        self.assertIn("list_filter = (", self.operations)
        self.assertIn("inlines = (TodoCommentInline,)", self.operations)
        self.assertIn("class TodoCommentInline", self.operations)
        self.assertIn("can_delete = False", self.operations)

    def test_communication_admin_exposes_immutable_revision_history_inline(self):
        self.assertIn("class CommunicationLogAdmin", self.operations)
        self.assertIn("inlines = (CommunicationLogRevisionInline,)", self.operations)
        self.assertIn("class CommunicationLogRevisionInline", self.operations)

    def test_messaging_relations_are_inline(self):
        self.assertIn(
            "inlines = (MessageInline, ConversationParticipantStateInline)",
            self.messaging,
        )
        self.assertIn("inlines = (MessageAttachmentInline,)", self.messaging)

    def test_student_applications_are_inline(self):
        self.assertIn("class ApplicationInline", self.students)
        self.assertIn(
            "inlines = (StudentDocumentInline, ApplicationInline)",
            self.students,
        )
