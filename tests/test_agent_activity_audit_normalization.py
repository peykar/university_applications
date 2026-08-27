from pathlib import Path

from django import forms
from django.conf import settings
from django.test import SimpleTestCase

from apps.geography.models import Country
from apps.leads.models import LeadActivityType
from apps.leads.services.activity import audit_form_value


class AgentActivityAuditNormalizationTests(SimpleTestCase):
    def test_model_choice_instance_uses_human_label(self):
        country = Country()
        country.__dict__["country_name"] = "Netherlands"
        field = forms.ModelChoiceField(queryset=Country.objects.none())
        self.assertEqual(audit_form_value(field, country), str(country))

    def test_choice_value_uses_display_label(self):
        field = forms.ChoiceField(choices=(("male", "Male"), ("female", "Female")))
        self.assertEqual(audit_form_value(field, "male"), "Male")

    def test_boolean_value_is_human_readable(self):
        field = forms.BooleanField(required=False)
        self.assertEqual(audit_form_value(field, True), "Yes")
        self.assertEqual(audit_form_value(field, False), "No")

    def test_dedicated_activity_types_exist(self):
        self.assertEqual(
            LeadActivityType.APPLICANT_UPDATED.label,
            "Applicant data updated",
        )
        self.assertEqual(
            LeadActivityType.INTERNAL_NOTES_UPDATED.label,
            "Internal notes updated",
        )

    def test_noop_normalized_changes_are_skipped(self):
        root = Path(settings.BASE_DIR)
        activity_service = (root / "apps/leads/services/activity.py").read_text(encoding="utf-8")
        self.assertIn("if old_value == new_value:", activity_service)
        self.assertIn("LeadActivityType.APPLICANT_UPDATED", activity_service)

    def test_model_choice_without_queryset_falls_back_safely(self):
        field = forms.ModelChoiceField(queryset=Country.objects.none())
        field.queryset = None
        self.assertEqual(audit_form_value(field, "abc"), "abc")
