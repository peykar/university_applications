from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentActivityPageTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.detail = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.activity = (root / "templates" / "agents" / "applicant_activity.html").read_text(
            encoding="utf-8"
        )

    def test_activity_has_dedicated_route_and_page(self):
        self.assertIn("def applicant_activity", self.views)
        self.assertIn('name="agent-applicant-activity"', self.urls)
        self.assertIn("Applicant audit log", self.activity)

    def test_activity_removed_from_main_applicant_page(self):
        self.assertNotIn('id="activity"', self.detail)
        self.assertIn("agent-applicant-activity", self.detail)

    def test_internal_notes_privacy_hint_is_compact(self):
        self.assertIn('class="private-badge"', self.detail)
        self.assertIn("Visible only to agent/staff users.", self.detail)
        self.assertNotIn(
            "Visible to agent/staff users only — never shown to the applicant.",
            self.detail,
        )
