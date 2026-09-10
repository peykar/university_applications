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


class BusinessEmailContentTests(SimpleTestCase):
    def test_request_received_preview_and_delivery_share_content_builder(self):
        from apps.core.services.business_email_content import build_business_email_content

        content = build_business_email_content(
            "request_received",
            name="Sample Student",
            url="https://turkdemy.com/en/requests/42/",
        )
        self.assertEqual(content.subject, "We received your TurkDemy request")
        self.assertEqual(content.cta_label, "View your request")
        self.assertEqual(content.cta_url, "https://turkdemy.com/en/requests/42/")
        self.assertIn("Hello Sample Student,", content.text_body)
        self.assertIn("We received your request.", content.text_body)
        self.assertIn("https://turkdemy.com/en/requests/42/", content.text_body)

    def test_unknown_business_email_type_is_rejected(self):
        from apps.core.services.business_email_content import build_business_email_content

        with self.assertRaises(ValueError):
            build_business_email_content("not-a-real-email")


class BusinessEmailBrandAndLinkTests(SimpleTestCase):
    def test_persian_subject_uses_localized_brand(self):
        from django.utils import translation

        from apps.core.services.business_email_content import build_business_email_content

        with translation.override("fa"):
            content = build_business_email_content(
                "request_received",
                name="Sample Student",
                url="https://turkdemy.com/fa/requests/42/",
            )
        self.assertIn("ترک‌دمی", content.subject)
        self.assertNotIn("TurkDemy", content.subject)

    def test_business_html_renders_clickable_cta(self):
        from apps.core.services.email_branding import render_branded_email_html

        html = render_branded_email_html(
            subject="Subject",
            text_body="Body",
            cta_label="View request",
            cta_url="https://turkdemy.com/en/requests/42/",
        )
        self.assertIn('href="https://turkdemy.com/en/requests/42/"', html)
        self.assertIn("View request", html)
