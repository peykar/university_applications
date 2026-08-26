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
