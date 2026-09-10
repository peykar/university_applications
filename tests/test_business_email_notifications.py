from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from apps.core.email_previews import EMAIL_PREVIEW_REGISTRY
from apps.core.services.business_email import notify_todo_assigned

BUSINESS_TYPES = {
    "request_received",
    "new_request_agent",
    "new_message_customer",
    "new_message_agent",
    "program_recommended",
    "document_action_required",
    "request_moving_forward",
    "application_started",
    "application_status_updated",
    "todo_assigned",
}


class BusinessEmailRegistryTests(SimpleTestCase):
    def test_all_business_email_types_are_registered(self):
        self.assertTrue(BUSINESS_TYPES.issubset(EMAIL_PREVIEW_REGISTRY))

    def test_business_email_types_have_categories_and_template_prefixes(self):
        for key in BUSINESS_TYPES:
            spec = EMAIL_PREVIEW_REGISTRY[key]
            self.assertTrue(spec.category)
            self.assertTrue(spec.template_prefix.startswith("emails/business/"))


class TodoEmailPolicyTests(SimpleTestCase):
    @patch("apps.core.services.business_email.transaction.on_commit")
    def test_self_assigned_todo_does_not_schedule_email(self, on_commit):
        todo = SimpleNamespace(assignee_id=7, created_by_id=7)
        notify_todo_assigned(todo, performed_by=SimpleNamespace(pk=7))
        on_commit.assert_not_called()

    @patch("apps.core.services.business_email.transaction.on_commit")
    def test_todo_assigned_to_other_user_schedules_post_commit_email(self, on_commit):
        todo = SimpleNamespace(
            assignee_id=8,
            created_by_id=7,
            assignee=Mock(email="agent@example.com"),
            title="Review applicant",
            due_date=None,
        )
        notify_todo_assigned(todo, performed_by=SimpleNamespace(pk=7))
        on_commit.assert_called_once()
