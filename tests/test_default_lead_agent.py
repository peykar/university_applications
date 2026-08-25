from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.agents.models import Agent
from apps.leads.models import Lead


class DefaultLeadAgentTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="lead-owner",
            email="lead-owner@example.com",
            password="test-password",
        )
        self.default_agent = Agent.objects.create(
            company_name="Default Agent",
            is_active=True,
        )
        self.other_agent = Agent.objects.create(
            company_name="Explicit Agent",
            is_active=True,
        )

    def test_new_unassigned_lead_gets_configured_default_agent(self):
        with override_settings(DEFAULT_LEAD_AGENT_ID=str(self.default_agent.pk)):
            lead = Lead.objects.create(
                user=self.user,
                first_name="Ada",
                last_name="Applicant",
            )

        self.assertEqual(lead.agent, self.default_agent)

    def test_explicit_agent_is_not_overwritten(self):
        with override_settings(DEFAULT_LEAD_AGENT_ID=str(self.default_agent.pk)):
            lead = Lead.objects.create(
                user=self.user,
                agent=self.other_agent,
                first_name="Ada",
                last_name="Applicant",
            )

        self.assertEqual(lead.agent, self.other_agent)

    @override_settings(DEFAULT_LEAD_AGENT_ID="")
    def test_empty_setting_leaves_lead_unassigned(self):
        lead = Lead.objects.create(
            user=self.user,
            first_name="Ada",
            last_name="Applicant",
        )

        self.assertIsNone(lead.agent)

    def test_inactive_configured_agent_is_not_assigned(self):
        self.default_agent.is_active = False
        self.default_agent.save(update_fields=("is_active", "updated_at"))

        with override_settings(DEFAULT_LEAD_AGENT_ID=str(self.default_agent.pk)):
            lead = Lead.objects.create(
                user=self.user,
                first_name="Ada",
                last_name="Applicant",
            )

        self.assertIsNone(lead.agent)

    @override_settings(DEFAULT_LEAD_AGENT_ID="00000000-0000-0000-0000-000000000000")
    def test_missing_configured_agent_leaves_lead_unassigned(self):
        lead = Lead.objects.create(
            user=self.user,
            first_name="Ada",
            last_name="Applicant",
        )

        self.assertIsNone(lead.agent)
