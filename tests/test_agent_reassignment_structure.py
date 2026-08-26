from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentReassignmentStructureTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.template = (root / "templates/agents/applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_reassignment_target_is_limited_to_lead_agent_users(self):
        self.assertIn(
            "target_user = lead.agent.users.filter(",
            self.views,
        )
        self.assertIn("is_active=True", self.views)

    def test_reassignment_has_dedicated_post_route(self):
        self.assertIn("views.applicant_assign", self.urls)
        self.assertIn('name="agent-applicant-assign"', self.urls)

    def test_reassignment_ui_uses_agent_users_only(self):
        self.assertIn("{% for agent_user in agent_users %}", self.template)
        self.assertIn('name="user_id"', self.template)
