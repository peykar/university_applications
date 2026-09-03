from pathlib import Path

from django.test import SimpleTestCase
from django.utils.translation import override

from apps.leads.models import LeadActivity, LeadActivityType


class ActivityLocalizationTests(SimpleTestCase):
    def _activity(self, *, activity_type, description, metadata=None):
        return LeadActivity(
            activity_type=activity_type,
            description=description,
            metadata=metadata or {},
        )

    def test_legacy_static_activity_uses_viewer_locale(self):
        activity = self._activity(
            activity_type=LeadActivityType.CREATED,
            description="Applicant profile created.",
        )

        with override("fa"):
            self.assertEqual(activity.localized_description, "پروفایل متقاضی ایجاد شد.")
        with override("tr"):
            self.assertEqual(
                activity.localized_description,
                "Başvuru sahibi profili oluşturuldu.",
            )
        with override("ar"):
            self.assertEqual(activity.localized_description, "تم إنشاء ملف المتقدم.")

    def test_legacy_dynamic_activity_localizes_sentence_and_preserves_value(self):
        activity = self._activity(
            activity_type=LeadActivityType.PROGRAM_ADDED,
            description="Program added: Artificial Intelligence.",
        )

        with override("fa"):
            self.assertEqual(
                activity.localized_description,
                "رشته اضافه شد: Artificial Intelligence.",
            )

    def test_structured_finalization_renders_without_stored_sentence(self):
        activity = self._activity(
            activity_type=LeadActivityType.FINALIZED,
            description="",
            metadata={
                "action": "finalized",
                "student_id": "student-123",
                "new_application_count": 2,
                "reopened": False,
            },
        )

        with override("fa"):
            rendered = activity.localized_description

        self.assertIn("student-123", rendered)
        self.assertIn("2", rendered)
        self.assertNotIn("Finalized and converted", rendered)

    def test_structured_change_field_labels_follow_viewer_locale(self):
        activity = self._activity(
            activity_type=LeadActivityType.APPLICANT_UPDATED,
            description="",
            metadata={
                "changes": [
                    {
                        "field": "middle_name",
                        "label": "Middle name",
                        "old": "—",
                        "new": "Ali",
                    }
                ]
            },
        )

        with override("fa"):
            changes = activity.localized_changes

        self.assertEqual(changes[0]["label"], "نام میانی")
        self.assertEqual(changes[0]["old"], "—")
        self.assertEqual(changes[0]["new"], "Ali")

    def test_unknown_free_form_activity_description_is_preserved(self):
        activity = self._activity(
            activity_type=LeadActivityType.NOTE,
            description="Call the applicant again on Monday.",
        )

        with override("fa"):
            self.assertEqual(
                activity.localized_description,
                "Call the applicant again on Monday.",
            )

    def test_agent_activity_template_uses_localized_description(self):
        template = Path("templates/agents/applicant_activity.html").read_text()

        self.assertIn("activity.localized_description", template)
        self.assertNotIn("<p>{{ activity.description }}</p>", template)
