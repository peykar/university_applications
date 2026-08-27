from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.agents.models import Agent
from apps.agents.services.context import ACTIVE_AGENT_SESSION_KEY
from apps.leads.models import Lead


class MultiAgentContextTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.agent_user = user_model.objects.create_user(
            username="multi-agent",
            email="multi-agent@example.com",
            password="test-password",
        )
        self.customer = user_model.objects.create_user(
            username="customer-multi",
            email="customer-multi@example.com",
            password="test-password",
        )
        self.agent_a = Agent.objects.create(company_name="Alpha Education")
        self.agent_b = Agent.objects.create(company_name="Beta Education")
        self.agent_a.users.add(self.agent_user)
        self.agent_b.users.add(self.agent_user)
        self.lead_a = Lead.objects.create(
            user=self.customer,
            agent=self.agent_a,
            first_name="Alpha",
            last_name="Applicant",
        )
        self.lead_b = Lead.objects.create(
            user=self.customer,
            agent=self.agent_b,
            first_name="Beta",
            last_name="Applicant",
        )
        self.client.force_login(self.agent_user)

    def activate(self, agent):
        session = self.client.session
        session[ACTIVE_AGENT_SESSION_KEY] = str(agent.pk)
        session.save()

    def test_single_membership_is_selected_automatically(self):
        self.agent_b.users.remove(self.agent_user)
        response = self.client.get(reverse("agent-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.session[ACTIVE_AGENT_SESSION_KEY],
            str(self.agent_a.pk),
        )
        self.assertContains(response, "Alpha Education")

    def test_first_multi_agent_entry_requires_explicit_choice(self):
        response = self.client.get(reverse("agent-dashboard"))
        self.assertRedirects(response, reverse("agent-choose"))
        response = self.client.get(reverse("agent-choose"))
        self.assertContains(response, "Alpha Education")
        self.assertContains(response, "Beta Education")

    def test_switching_agent_changes_workspace_scope(self):
        response = self.client.post(
            reverse("agent-switch"),
            {"agent_id": str(self.agent_b.pk), "next": reverse("agent-dashboard")},
        )
        self.assertRedirects(response, reverse("agent-dashboard"))

        response = self.client.get(reverse("agent-dashboard"))
        self.assertContains(response, "Beta Education")
        self.assertContains(response, "Beta Applicant")
        self.assertNotContains(response, "Alpha Applicant")

    def test_active_agent_blocks_other_membership_records(self):
        session = self.client.session
        session[ACTIVE_AGENT_SESSION_KEY] = str(self.agent_a.pk)
        session.save()

        response = self.client.get(reverse("agent-applicant-detail", args=[self.lead_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_tampered_session_agent_is_revalidated(self):
        outsider = Agent.objects.create(company_name="Outsider")
        session = self.client.session
        session[ACTIVE_AGENT_SESSION_KEY] = str(outsider.pk)
        session.save()

        response = self.client.get(reverse("agent-dashboard"))
        self.assertRedirects(response, reverse("agent-choose"))
        self.assertNotIn(ACTIVE_AGENT_SESSION_KEY, self.client.session)

    def test_switch_rejects_agent_without_membership(self):
        outsider = Agent.objects.create(company_name="Outsider")
        response = self.client.post(
            reverse("agent-switch"),
            {"agent_id": str(outsider.pk)},
        )
        self.assertEqual(response.status_code, 403)

    def test_sidebar_uses_logo_when_agent_has_one(self):
        self.activate(self.agent_a)
        response = self.client.get(reverse("agent-dashboard"))
        self.assertContains(response, "agent-sidebar-logo")
        self.assertContains(response, "Alpha Education")

    def test_sidebar_shows_agent_identity_and_switcher(self):
        session = self.client.session
        session[ACTIVE_AGENT_SESSION_KEY] = str(self.agent_a.pk)
        session.save()
        response = self.client.get(reverse("agent-dashboard"))
        self.assertContains(response, "Alpha Education")
        self.assertContains(response, "Switch organization")
        self.assertNotContains(response, 'class="workspace-sidebar-eyebrow"')
