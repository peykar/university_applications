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
        self.forms = (root / "apps" / "agents" / "forms.py").read_text(encoding="utf-8")
        self.edit_template = (root / "templates" / "agents" / "applicant_edit.html").read_text(
            encoding="utf-8"
        )
        self.customer_detail = (root / "templates" / "leads" / "lead_detail.html").read_text(
            encoding="utf-8"
        )
        self.customer_section = (root / "templates" / "leads" / "lead_section.html").read_text(
            encoding="utf-8"
        )

    def test_internal_notes_are_visible_in_agent_workspace(self):
        self.assertIn('id="internal-notes"', self.detail_template)
        self.assertIn('class="private-badge"', self.detail_template)
        self.assertIn("Visible only to agent/staff users.", self.detail_template)
        self.assertIn("lead.notes", self.detail_template)
        self.assertIn("Applicant record last updated", self.detail_template)

        self.assertLess(
            self.detail_template.index('id="internal-notes"'),
            self.detail_template.index("<aside>"),
        )

    def test_internal_notes_are_not_applicant_profile_fields(self):
        form_block = self.forms.split(
            "class AgentLeadEditForm(LocalizedFormMixin, forms.ModelForm):",
            1,
        )[1].split("class StudentRecordConversionForm", 1)[0]
        self.assertNotIn('"notes"', form_block)
        self.assertNotIn("Internal notes", self.edit_template)

    def test_internal_notes_never_render_in_customer_applicant_templates(self):
        self.assertNotIn("lead.notes", self.customer_detail)
        self.assertNotIn("lead.notes", self.customer_section)

    def test_internal_notes_have_dedicated_update_endpoint(self):
        self.assertIn("def applicant_internal_notes", self.views)
        self.assertIn('name="agent-applicant-internal-notes"', self.urls)
        self.assertIn("LeadActivityType.INTERNAL_NOTES_UPDATED", self.views)
        note_block = self.views.split("def applicant_internal_notes", 1)[1].split(
            "def applicant_edit",
            1,
        )[0]
        self.assertIn("is_customer_visible=False", note_block)

    def test_activity_timeline_is_on_dedicated_page(self):
        self.assertNotIn('id="activity"', self.detail_template)
        self.assertIn("agent-applicant-activity", self.detail_template)
        self.assertIn("activity.get_activity_type_display", self.activity_template)
        self.assertIn("activity.created_by", self.activity_template)
        self.assertIn("activity.localized_description", self.activity_template)
        self.assertIn("activity.localized_changes", self.activity_template)

    def test_activity_queryset_includes_actor(self):
        self.assertIn(
            'lead.activities.select_related("created_by")',
            self.views,
        )

    def test_activity_changes_are_structured(self):
        self.assertIn('"changes": [', self.views)
        self.assertIn('"field": "notes"', self.views)
        self.assertIn('"old": old_notes or "—"', self.views)
        self.assertIn('"new": new_notes or "—"', self.views)
        self.assertIn('class="activity-change-row"', self.activity_template)

    def test_customer_visible_badge_is_on_activity_page(self):
        self.assertNotIn(
            '<span class="activity-visibility internal">',
            self.activity_template,
        )
        self.assertIn("Customer visible", self.activity_template)
