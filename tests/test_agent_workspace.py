from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.agents.models import Agent
from apps.leads.models import (
    Lead,
    LeadMessage,
    LeadMessageSenderType,
)


class AgentWorkspaceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.agent_user = user_model.objects.create_user(
            username="agent",
            email="agent@example.com",
            password="test-password",
        )
        self.customer = user_model.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="test-password",
        )
        self.other_agent_user = user_model.objects.create_user(
            username="other-agent",
            email="other-agent@example.com",
            password="test-password",
        )

        self.agent = Agent.objects.create(company_name="Primary Agent")
        self.agent.users.add(self.agent_user)
        self.other_agent = Agent.objects.create(company_name="Other Agent")
        self.other_agent.users.add(self.other_agent_user)

        self.lead = Lead.objects.create(
            user=self.customer,
            agent=self.agent,
            first_name="Ada",
            last_name="Applicant",
        )
        self.other_lead = Lead.objects.create(
            user=self.customer,
            agent=self.other_agent,
            first_name="Other",
            last_name="Applicant",
        )
        conversation = self.lead.conversation
        LeadMessage.objects.create(
            conversation=conversation,
            sender=self.customer,
            sender_type=LeadMessageSenderType.CUSTOMER,
            body="I need help with my application.",
        )

    def test_non_agent_cannot_open_agent_workspace(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("agent-dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_agent_dashboard_contains_only_its_applicants(self):
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse("agent-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ada Applicant")
        self.assertNotContains(response, "Other Applicant")

    def test_agent_cannot_open_another_agents_applicant(self):
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse("agent-applicant-detail", args=[self.other_lead.pk]))
        self.assertEqual(response.status_code, 404)

    def test_opening_applicant_marks_customer_message_read(self):
        self.client.force_login(self.agent_user)
        response = self.client.get(reverse("agent-applicant-detail", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 200)
        message = self.lead.conversation.messages.get()
        self.assertTrue(message.read_receipts.filter(user=self.agent_user).exists())

    def test_agent_can_reply_to_customer(self):
        self.client.force_login(self.agent_user)
        response = self.client.post(
            reverse("agent-applicant-message", args=[self.lead.pk]),
            {"body": "We are reviewing it."},
        )
        self.assertRedirects(
            response,
            reverse("agent-applicant-detail", args=[self.lead.pk]),
        )
        reply = self.lead.conversation.messages.order_by("-created_at").first()
        self.assertEqual(reply.sender_type, LeadMessageSenderType.STAFF)
        self.assertEqual(reply.sender, self.agent_user)

    def test_agent_program_names_link_to_public_program_page(self):
        template = (
            Path(__file__).resolve().parents[1] / "templates" / "agents" / "applicant_detail.html"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "href=\"{% url 'program-detail' interest.program.slug_en %}\"",
            template,
        )
        self.assertIn("agent-program-link", template)
