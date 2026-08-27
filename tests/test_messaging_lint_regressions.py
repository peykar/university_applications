from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MessagingLintRegressionTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.lead_views = (root / "apps/leads/views.py").read_text(encoding="utf-8")
        self.services = (root / "apps/messaging/services.py").read_text(encoding="utf-8")

    def test_messaging_imports_are_before_lead_view_functions(self):
        import_position = self.lead_views.index("from apps.messaging.forms import MessageForm")
        first_view_position = self.lead_views.index("\ndef ")
        self.assertLess(import_position, first_view_position)

    def test_agent_permission_check_is_not_nested(self):
        self.assertIn(
            "sender_role == MessageSenderRole.AGENT and not can_access_as_agent",
            self.services,
        )
