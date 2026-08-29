from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.leads.models import Lead
from apps.messaging.models import Conversation


@override_settings(DEFAULT_LEAD_AGENT_ID="")
class UnassignedCustomerRequestTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="unassigned-customer",
            email="unassigned@example.com",
            password="test-password",
        )
        self.lead = Lead.objects.create(
            user=self.user,
            first_name="Unassigned",
            last_name="Customer",
            email=self.user.email,
            created_by=self.user,
            updated_by=self.user,
        )
        self.client.force_login(self.user)

    def test_request_detail_renders_without_agent_or_conversation(self):
        self.assertIsNone(self.lead.agent)

        response = self.client.get(reverse("lead-detail", kwargs={"lead_id": self.lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["conversation"])
        self.assertEqual(response.context["unread_message_count"], 0)
        self.assertFalse(
            Conversation.objects.filter(
                customer=self.user,
                subject_object_id=self.lead.pk,
            ).exists()
        )

    def test_messages_tab_waits_for_advisor_assignment(self):
        response = self.client.get(reverse("lead-messages", kwargs={"lead_id": self.lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Messaging will become available once TurkDemy assigns an advisor to this Request.",
        )
        self.assertNotContains(response, 'class="chat-compose"')

    def test_message_post_is_safe_before_advisor_assignment(self):
        response = self.client.post(
            reverse("lead-send-message", kwargs={"lead_id": self.lead.pk}),
            {"body": "Hello"},
        )

        self.assertRedirects(
            response,
            reverse("lead-messages", kwargs={"lead_id": self.lead.pk}),
        )
        self.assertFalse(
            Conversation.objects.filter(
                customer=self.user,
                subject_object_id=self.lead.pk,
            ).exists()
        )
