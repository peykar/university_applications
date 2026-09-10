from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.agents.models import Agent
from apps.leads.models import Lead
from apps.messaging.models import Message, MessageSenderRole
from apps.messaging.services import get_or_create_conversation


class ApplicantMessagingCanonicalUITests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.agent_user = user_model.objects.create_user(
            username="agent-canonical",
            email="agent-canonical@example.com",
            password="test-password",
            first_name="Ava",
            last_name="Advisor",
        )
        self.customer = user_model.objects.create_user(
            username="customer-canonical",
            email="customer-canonical@example.com",
            password="test-password",
            first_name="Sam",
            last_name="Student",
        )
        self.agent = Agent.objects.create(company_name="Canonical Agent")
        self.agent.users.add(self.agent_user)
        self.lead = Lead.objects.create(
            user=self.customer,
            agent=self.agent,
            first_name="Sam",
            last_name="Student",
        )
        conversation = get_or_create_conversation(subject=self.lead)
        Message.objects.create(
            conversation=conversation,
            sender=self.customer,
            sender_role=MessageSenderRole.CUSTOMER,
            body="Hello from the customer.",
        )
        self.client.force_login(self.agent_user)

    def test_overview_and_messages_route_use_same_conversation_component(self):
        project_root = Path(__file__).resolve().parents[1]
        overview = (project_root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )
        section = (project_root / "templates/agents/applicant_section.html").read_text(
            encoding="utf-8"
        )
        include = '{% include "agents/includes/applicant_conversation.html" %}'
        self.assertIn(include, overview)
        self.assertIn(include, section)
        self.assertNotIn('class="agent-chat"', overview)

    def test_both_surfaces_render_canonical_message_markup_and_sender_name(self):
        for route_name in ("agent-applicant-detail", "agent-applicant-messages"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name, args=[self.lead.pk]))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="lead-chat applicant-conversation"')
                self.assertContains(response, "Sam Student")
                self.assertContains(response, "Hello from the customer.")
                self.assertContains(response, "Send reply")
