from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AtomicLeadFinalizationTests(SimpleTestCase):
    def setUp(self):
        root = Path(settings.BASE_DIR)
        self.conversion = (root / "apps/leads/services/conversion.py").read_text(encoding="utf-8")
        self.views = (root / "apps/agents/views.py").read_text(encoding="utf-8")

    def test_agent_finalize_is_one_business_operation(self):
        self.assertIn(
            "student = finalize_lead(lead, performed_by=request.user)",
            self.views,
        )
        self.assertNotIn(
            "student = convert_lead_to_student(lead, performed_by=request.user)",
            self.views,
        )

    def test_finalization_service_is_atomic(self):
        self.assertIn("@transaction.atomic\ndef finalize_lead(", self.conversion)
        self.assertIn("_validate_for_finalization(lead)", self.conversion)
        self.assertIn("student = Student.objects.create(", self.conversion)
        self.assertIn("_copy_verified_documents(", self.conversion)
        self.assertIn("lead.status = LeadStatus.FINALIZED", self.conversion)

    def test_no_intermediate_validated_activity_or_message(self):
        self.assertNotIn(
            "Applicant data validated and ready for conversion.",
            self.conversion,
        )
        self.assertNotIn(
            "profile has been validated and is ready for conversion",
            self.conversion,
        )

    def test_legacy_conversion_name_is_only_an_alias(self):
        self.assertIn(
            "convert_lead_to_student = finalize_lead",
            self.conversion,
        )
