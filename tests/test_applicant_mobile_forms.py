from pathlib import Path

from django.conf import settings
from django.test import TestCase

from apps.leads.forms import LeadPreferenceForm


class ApplicantMobileFormTests(TestCase):
    def setUp(self):
        base = Path(settings.BASE_DIR)
        self.preferences = (base / "templates" / "leads" / "lead_preferences.html").read_text(
            encoding="utf-8"
        )
        self.css = (base / "static" / "css" / "turkdemy.css").read_text(encoding="utf-8")

    def test_large_preference_fields_use_searchable_multiselect(self):
        form = LeadPreferenceForm()
        for name in (
            "preferred_languages",
            "preferred_cities",
            "preferred_universities",
            "preferred_departments",
        ):
            self.assertIn(
                "searchable-multiselect",
                form.fields[name].widget.attrs.get("class", ""),
            )

    def test_preferences_are_grouped_not_rendered_with_as_p(self):
        self.assertNotIn("{{ form.as_p }}", self.preferences)
        self.assertIn("applicant-form-section", self.preferences)

    def test_mobile_form_grid_collapses_to_one_column(self):
        self.assertIn(".applicant-form-grid,", self.css)
        self.assertIn("grid-template-columns:1fr!important;", self.css)
