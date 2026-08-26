from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.agents.models import Agent
from apps.leads.models import Lead


class FancyAgentNotFoundTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.agent_user = user_model.objects.create_user(
            username="agent-404",
            email="agent-404@example.com",
            password="test-password",
        )
        self.customer = user_model.objects.create_user(
            username="customer-404",
            email="customer-404@example.com",
            password="test-password",
        )
        self.agent = Agent.objects.create(company_name="404 Agent")
        self.agent.users.add(self.agent_user)

    def test_missing_agent_applicant_uses_polished_404(self):
        self.client.force_login(self.agent_user)
        response = self.client.get(
            reverse(
                "agent-applicant-detail",
                args=["00000000-0000-0000-0000-000000000000"],
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")
        self.assertContains(
            response,
            "isn't available in your agent workspace",
            status_code=404,
        )

    def test_other_agents_applicant_does_not_leak_existence(self):
        other_agent = Agent.objects.create(company_name="Other 404 Agent")
        lead = Lead.objects.create(
            user=self.customer,
            agent=other_agent,
            first_name="Hidden",
            last_name="Applicant",
        )

        self.client.force_login(self.agent_user)
        response = self.client.get(reverse("agent-applicant-detail", args=[lead.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "errors/404.html")
        self.assertNotContains(
            response,
            "Hidden Applicant",
            status_code=404,
        )
