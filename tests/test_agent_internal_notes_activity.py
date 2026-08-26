from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentInternalNotesActivityTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.detail_template = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )
        self.activity_template = (
            root / "templates" / "agents" / "applicant_activity.html"
        ).read_text(encoding="utf-8")

    def test_internal_notes_are_visible_in_agent_workspace(self):
        self.assertIn('id="internal-notes"', self.detail_template)
        self.assertIn('class="private-badge"', self.detail_template)
        self.assertIn("Visible only to agent/staff users.", self.detail_template)
        self.assertIn("lead.notes", self.detail_template)

    def test_internal_notes_have_dedicated_update_endpoint(self):
        self.assertIn("def applicant_internal_notes", self.views)
        self.assertIn('name="agent-applicant-internal-notes"', self.urls)
        self.assertIn("LeadActivityType.INTERNAL_NOTES_UPDATED", self.views)

    def test_activity_timeline_is_on_dedicated_page(self):
        self.assertNotIn('id="activity"', self.detail_template)
        self.assertIn("agent-applicant-activity", self.detail_template)
        self.assertIn("activity.get_activity_type_display", self.activity_template)
        self.assertIn("activity.created_by", self.activity_template)
        self.assertIn("activity.description", self.activity_template)
        self.assertIn("activity.metadata.changes", self.activity_template)

    def test_activity_queryset_includes_actor(self):
        self.assertIn(
            'lead.activities.select_related("created_by")',
            self.views,
        )

    def test_activity_changes_are_structured(self):
        self.assertIn('metadata={"changes": changes}', self.views)
        self.assertIn('class="activity-change-row"', self.activity_template)

    def test_customer_visible_badge_is_on_activity_page(self):
        self.assertNotIn(
            '<span class="activity-visibility internal">',
            self.activity_template,
        )
        self.assertIn("Customer visible", self.activity_template)
