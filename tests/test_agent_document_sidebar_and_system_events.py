from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentDocumentSidebarAndSystemEventTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.template = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.conversation_template = (
            root / "templates" / "agents" / "includes" / "applicant_conversation.html"
        ).read_text(encoding="utf-8")
        self.css = (root / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

    def test_system_messages_use_compact_event_row(self):
        self.assertIn(
            'message.sender_role == "system"',
            self.conversation_template,
        )
        self.assertIn("system-event-row", self.conversation_template)
        self.assertIn(".agent-message.system-event", self.css)

    def test_document_filename_is_constrained_in_sidebar(self):
        self.assertIn(
            ".agent-document-summary .document-copy small",
            self.css,
        )
        self.assertIn("text-overflow:ellipsis", self.css)
        self.assertIn("grid-template-columns:minmax(0,1fr) auto", self.css)
