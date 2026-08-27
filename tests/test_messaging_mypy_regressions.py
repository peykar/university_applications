from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class MessagingMypyRegressionTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.models = (root / "apps/messaging/models.py").read_text(encoding="utf-8")
        self.command = (
            root / "apps/messaging/management/commands/migrate_legacy_messages.py"
        ).read_text(encoding="utf-8")

    def test_nullable_relations_are_narrowed_before_access(self):
        self.assertIn("content_type = self.subject_content_type", self.models)
        self.assertIn("if content_type is None:", self.models)
        self.assertIn("last_read_message = self.last_read_message", self.models)
        self.assertIn("last_read_message is not None", self.models)

    def test_migration_command_uses_lead_model_for_content_type(self):
        self.assertIn(
            "ContentType.objects.get_for_model(\n            Lead,",
            self.command,
        )

    def test_migration_command_has_explicit_collection_types(self):
        self.assertIn(
            "counters: defaultdict[str, int]",
            self.command,
        )
        self.assertIn(
            "conversation_map: dict[Any, Any]",
            self.command,
        )
        self.assertIn(
            "latest_receipts: dict[tuple[Any, Any], LeadMessageRead]",
            self.command,
        )

    def test_legacy_loop_variables_have_distinct_types(self):
        self.assertIn(
            "for legacy_conversation in legacy_conversations.iterator():",
            self.command,
        )
        self.assertIn(
            "for legacy_message in legacy_messages.iterator():",
            self.command,
        )
        self.assertIn(
            "for legacy_attachment in legacy_attachments.iterator():",
            self.command,
        )
