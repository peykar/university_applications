from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class LeadAssignmentLifecycleStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.models = (root / "apps/leads/models.py").read_text(encoding="utf-8")
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.detail = (root / "templates/agents/applicant_detail.html").read_text(encoding="utf-8")
        self.list_template = (root / "templates/agents/applicant_list.html").read_text(
            encoding="utf-8"
        )

    def test_statuses_are_minimal(self):
        block = self.models.split("class LeadStatus", 1)[1].split("class LeadSource", 1)[0]
        for value in ("NEW", "ASSIGNED", "FINALIZED", "CLOSED"):
            self.assertIn(value, block)
        for value in ("IN_REVIEW", "NEEDS_INFO", "CONVERTED", "REJECTED"):
            self.assertNotIn(value, block)

    def test_assignment_derives_status(self):
        self.assertIn("LeadStatus.ASSIGNED if self.assigned_to_id else LeadStatus.NEW", self.models)

    def test_agent_can_assign_to_self(self):
        self.assertIn("def applicant_assign_to_me", self.views)
        self.assertIn("agent-applicant-assign-to-me", self.detail)

    def test_responsible_user_is_visible(self):
        self.assertIn("Responsible", self.detail)
        self.assertIn("Responsible:", self.list_template)

    def test_manual_status_ui_is_only_close_or_reopen(self):
        self.assertNotIn("Workflow status", self.detail)
        self.assertIn('name="action" value="close"', self.detail)
        self.assertIn('name="action" value="reopen"', self.detail)

    def test_agent_can_reassign_to_agent_user(self):
        self.assertIn("def applicant_assign(request, lead_id)", self.views)
        self.assertIn(
            "lead.agent.users.filter(",
            self.views,
        )
        self.assertIn("agent-applicant-assign", self.detail)
        self.assertIn("Reassign", self.detail)

    def test_assignment_modal_explains_visibility_vs_responsibility(self):
        self.assertIn(
            "All users of the agent can still see this applicant",
            self.detail,
        )

    def test_current_responsible_user_shows_name_and_you(self):
        self.assertIn(
            "lead.assigned_to.get_full_name|default:lead.assigned_to.username",
            self.detail,
        )
        self.assertIn('({% trans "You" %})', self.detail)

    def test_close_applicant_uses_modal_action(self):
        self.assertIn('data-modal-target="close-applicant-modal"', self.detail)
        self.assertIn('id="close-applicant-modal"', self.detail)

    def test_responsibility_actions_are_grouped_with_responsible_agent(self):
        self.assertIn('class="responsibility-actions"', self.detail)
        self.assertIn('class="responsibility-action', self.detail)
        self.assertIn('class="agent-lifecycle-actions"', self.detail)
        self.assertIn("lifecycle-close-action", self.detail)
