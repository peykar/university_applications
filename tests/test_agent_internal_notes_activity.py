from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AgentInternalNotesActivityTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.urls = (root / "apps/agents/urls.py").read_text(encoding="utf-8")
        self.template = (root / "templates" / "agents" / "applicant_detail.html").read_text(
            encoding="utf-8"
        )

    def test_internal_notes_are_visible_in_agent_workspace(self):
        self.assertIn('id="internal-notes"', self.template)
        self.assertIn("Visible to agent/staff users only", self.template)
        self.assertIn("lead.notes", self.template)

    def test_internal_notes_have_dedicated_update_endpoint(self):
        self.assertIn("def applicant_internal_notes", self.views)
        self.assertIn('name="agent-applicant-internal-notes"', self.urls)
        self.assertIn("Internal notes updated.", self.views)

    def test_activity_timeline_is_rendered(self):
        self.assertIn('id="activity"', self.template)
        self.assertIn("activity.get_activity_type_display", self.template)
        self.assertIn("activity.created_by", self.template)
        self.assertIn("activity.description", self.template)
        self.assertIn("activity.metadata.changes", self.template)

    def test_activity_queryset_includes_actor(self):
        self.assertIn(
            'lead.activities.select_related("created_by")',
            self.views,
        )

    def test_activity_changes_are_structured_and_collapsible(self):
        self.assertIn('metadata={"changes": changes}', self.views)
        self.assertIn('class="activity-change-row"', self.template)
        self.assertIn("forloop.counter > 10", self.template)
        self.assertIn("data-activity-show-more", self.template)

    def test_internal_badge_is_not_repeated_on_every_activity(self):
        self.assertNotIn(
            '<span class="activity-visibility internal">',
            self.template,
        )
        self.assertIn("Customer visible", self.template)
