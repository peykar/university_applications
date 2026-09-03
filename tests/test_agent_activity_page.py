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
        self.css = (root / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

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

    def test_activity_metadata_stays_grouped_with_event_content(self):
        self.assertIn('class="activity-byline"', self.activity)
        self.assertIn('class="activity-actor" dir="auto"', self.activity)
        self.assertIn("<time>{{ activity.created_at|localized_datetime }}</time>", self.activity)

        activity_meta_css = self.css.split(".activity-meta{", 1)[1].split("}", 1)[0]
        self.assertIn("display:grid;", activity_meta_css)
        self.assertIn("justify-items:start;", activity_meta_css)
        self.assertIn("gap:3px;", activity_meta_css)
        self.assertNotIn("justify-content:space-between;", activity_meta_css)

    def test_activity_dynamic_content_is_bidi_safe(self):
        self.assertIn('class="activity-description" dir="auto"', self.activity)
        self.assertIn('class="activity-change-old" dir="auto"', self.activity)
        self.assertIn('class="activity-change-new" dir="auto"', self.activity)
        self.assertIn(".activity-description{", self.css)
        self.assertIn("unicode-bidi:plaintext;", self.css)
