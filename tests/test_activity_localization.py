from pathlib import Path
from unittest.mock import MagicMock, patch

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

    def test_structured_finalization_resolves_student_at_render_time(self):
        activity = self._activity(
            activity_type=LeadActivityType.FINALIZED,
            description="",
            metadata={
                "action": "finalized",
                "student_id": "39c41877-71c7-4b29-a8b3-95e9811968e1",
                "new_application_count": 2,
                "reopened": False,
            },
        )
        student = MagicMock()
        student.__str__.return_value = "Iman Karimi"

        with (
            patch("apps.students.models.Student.objects.filter") as filter_mock,
            override("fa"),
        ):
            filter_mock.return_value.first.return_value = student
            rendered = activity.localized_description

        self.assertIn("Iman Karimi", rendered)
        self.assertNotIn("39c41877-71c7-4b29-a8b3-95e9811968e1", rendered)
        self.assertIn("2", rendered)
        filter_mock.assert_called_once_with(pk="39c41877-71c7-4b29-a8b3-95e9811968e1")

    def test_structured_finalization_never_exposes_missing_student_uuid(self):
        student_id = "39c41877-71c7-4b29-a8b3-95e9811968e1"
        activity = self._activity(
            activity_type=LeadActivityType.FINALIZED,
            description=(
                f"Finalized and converted to Student {student_id}; created 0 draft application(s)."
            ),
            metadata={
                "student_id": student_id,
                "new_application_count": 0,
                "reopened": False,
            },
        )

        with (
            patch("apps.students.models.Student.objects.filter") as filter_mock,
            override("fa"),
        ):
            filter_mock.return_value.first.return_value = None
            rendered = activity.localized_description

        self.assertNotIn(student_id, rendered)
        self.assertIn("0", rendered)

    def test_finalization_activity_producer_keeps_student_id_out_of_description(self):
        source = Path("apps/leads/services/conversion.py").read_text()

        self.assertIn("activity_type=LeadActivityType.FINALIZED", source)
        self.assertIn('description=""', source)
        self.assertNotIn("Finalized and converted to Student {student.pk}", source)
        self.assertNotIn("Re-finalized existing Student {student.pk}", source)

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
