from types import SimpleNamespace
from uuid import UUID

from django.test import SimpleTestCase

from apps.leads.models import (
    LeadMessageAttachment,
    lead_message_attachment_upload_path,
)


class LeadMessageAttachmentPathTests(SimpleTestCase):
    def test_file_field_allows_long_storage_paths(self):
        field = LeadMessageAttachment._meta.get_field("file")
        self.assertEqual(field.max_length, 500)

    def test_storage_filename_is_bounded_and_keeps_extension(self):
        lead_id = UUID("136a03e9-766d-4c81-93fb-9895fb6f3a5a")
        message_id = UUID("3bee53c6-ec7f-4136-8d32-f46bf03d83b1")
        instance = SimpleNamespace(
            message=SimpleNamespace(
                conversation=SimpleNamespace(lead_id=lead_id),
            ),
            message_id=message_id,
        )

        path = lead_message_attachment_upload_path(
            instance,
            "a" * 240 + ".JPG",
        )

        self.assertTrue(path.startswith(f"leads/{lead_id}/messages/{message_id}/"))
        self.assertTrue(path.endswith(".jpg"))
        self.assertLess(len(path), 180)
        self.assertNotIn("a" * 40, path)
