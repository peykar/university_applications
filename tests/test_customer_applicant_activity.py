from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class CustomerApplicantActivityTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.customer_views = (root / "apps/leads/views.py").read_text(encoding="utf-8")
        self.agent_views = (root / "apps/agents/views.py").read_text(encoding="utf-8")
        self.activity_service = (root / "apps/leads/services/activity.py").read_text(
            encoding="utf-8"
        )

    def test_customer_edit_records_applicant_profile_activity(self):
        self.assertIn(
            "record_applicant_profile_update(",
            self.customer_views,
        )
        self.assertIn(
            "actor=request.user",
            self.customer_views,
        )

    def test_agent_and_customer_share_same_audit_service(self):
        self.assertIn(
            "record_applicant_profile_update(",
            self.agent_views,
        )
        self.assertNotIn(
            "def _audit_form_value",
            self.agent_views,
        )

    def test_activity_contains_only_actual_changed_fields(self):
        self.assertIn("for field_name in form.changed_data:", self.activity_service)
        self.assertIn("if old_value == new_value:", self.activity_service)
        self.assertIn('metadata={"changes": changes}', self.activity_service)

    def test_model_choices_are_human_readable(self):
        self.assertIn(
            "isinstance(field, forms.ModelChoiceField)",
            self.activity_service,
        )
        self.assertIn("return str(queryset.get(pk=value))", self.activity_service)

    def test_no_activity_is_created_for_no_op_submission(self):
        self.assertIn("if not changes:", self.activity_service)
        self.assertIn("return False", self.activity_service)

    def test_choice_field_is_narrowed_before_accessing_choices(self):
        self.assertIn(
            "if isinstance(field, forms.ChoiceField):",
            self.activity_service,
        )
        self.assertIn(
            "if queryset is None:",
            self.activity_service,
        )

    def test_choice_audit_uses_widget_normalized_choices(self):
        self.assertIn(
            "for choice_value, label in field.widget.choices:",
            self.activity_service,
        )
