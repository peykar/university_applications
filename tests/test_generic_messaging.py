from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class GenericMessagingStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.models = (root / "apps/messaging/models.py").read_text(encoding="utf-8")
        self.services = (root / "apps/messaging/services.py").read_text(encoding="utf-8")
        self.agent_views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.agent_base = (root / "templates/agents/base.html").read_text(encoding="utf-8")
        self.base = (root / "templates/base.html").read_text(encoding="utf-8")

    def test_conversation_is_agent_customer_and_generic_subject_scoped(self):
        self.assertIn("class Conversation(BaseModel)", self.models)
        self.assertIn("subject_content_type", self.models)
        self.assertIn("subject_object_id", self.models)
        self.assertIn("GenericForeignKey", self.models)

    def test_read_state_is_per_user_and_party_role(self):
        self.assertIn("class ConversationParticipantState", self.models)
        self.assertIn("last_read_message", self.models)
        self.assertIn("last_read_at", self.models)
        self.assertIn('fields=("conversation", "user", "participant_role")', self.models)

    def test_agent_and_customer_unread_counts_are_separate(self):
        self.assertIn("def agent_unread_count", self.services)
        self.assertIn("def customer_unread_count", self.services)
        self.assertIn("MessageSenderRole.CUSTOMER", self.services)
        self.assertIn("MessageSenderRole.AGENT", self.services)

    def test_student_and_application_have_message_actions(self):
        self.assertIn("def student_message", self.agent_views)
        self.assertIn("def application_message", self.agent_views)

    def test_navigation_exposes_unread_badges(self):
        self.assertIn("agent_unread_message_count", self.agent_base)
        self.assertIn("customer_unread_message_count", self.base)

    def test_customer_has_generic_conversation_page(self):
        messaging_views = (Path(settings.BASE_DIR) / "apps/messaging/views.py").read_text(
            encoding="utf-8"
        )
        messaging_urls = (Path(settings.BASE_DIR) / "apps/messaging/urls.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("def customer_conversation_detail", messaging_views)
        self.assertIn("def customer_conversation_send", messaging_views)
        self.assertIn('name="customer-conversation-detail"', messaging_urls)
