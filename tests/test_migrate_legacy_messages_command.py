from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class LegacyMessageMigrationCommandTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.command = (
            root / "apps/messaging/management/commands/migrate_legacy_messages.py"
        ).read_text(encoding="utf-8")
        self.makefile = (root / "Makefile").read_text(encoding="utf-8")

    def test_command_is_idempotent(self):
        self.assertIn("Conversation.objects.get_or_create(", self.command)
        self.assertIn("Message.objects.get_or_create(", self.command)
        self.assertIn("MessageAttachment.objects.get_or_create(", self.command)
        self.assertIn("ConversationParticipantState.objects.update_or_create(", self.command)

    def test_command_supports_dry_run(self):
        self.assertIn('"--dry-run"', self.command)
        self.assertIn("transaction.set_rollback(True)", self.command)

    def test_read_receipts_become_participant_cursor(self):
        self.assertIn("latest_receipts", self.command)
        self.assertIn('"last_read_message_id": receipt.message_id', self.command)
        self.assertIn('"last_read_at": receipt.read_at', self.command)

    def test_makefile_exposes_commands(self):
        self.assertIn("messages-migrate:", self.makefile)
        self.assertIn("manage.py migrate_legacy_messages", self.makefile)
        self.assertIn("messages-migrate-dry-run:", self.makefile)
