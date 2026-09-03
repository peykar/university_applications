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
        self.assertIn("Applicant activity", self.activity)

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

    def test_activity_page_has_context_filters_and_pagination(self):
        self.assertIn("Responsible:", self.activity)
        self.assertIn("Assignment & status", self.activity)
        self.assertIn("activity_filter", self.activity)
        self.assertIn("activity_page.paginator", self.activity)

    def test_activity_view_uses_filtered_pagination(self):
        self.assertIn("filter_map = {", self.views)
        self.assertIn("Paginator(activities, 25)", self.views)
        self.assertIn("activity_type__in=filter_map[activity_filter]", self.views)

    def test_activity_page_has_notes_filter(self):
        self.assertIn('href="?type=notes"', self.activity)
        self.assertIn('{% trans "Notes" %}', self.activity)
        self.assertIn('"notes": (', self.views)
        self.assertIn("LeadActivityType.NOTE", self.views)
        self.assertIn("LeadActivityType.INTERNAL_NOTES_UPDATED", self.views)

    def test_program_suggestion_activity_shows_recommendation_reason(self):
        self.assertIn(
            'activity.activity_type == "program_suggested"',
            self.activity,
        )
        self.assertIn("activity.metadata.suggestion_reason", self.activity)
        self.assertIn('class="activity-recommendation-reason" dir="auto"', self.activity)
