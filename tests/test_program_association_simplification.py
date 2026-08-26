from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ProgramAssociationSimplificationTests(SimpleTestCase):
    def test_interest_model_has_no_status_field(self):
        source = (Path(settings.BASE_DIR) / "apps" / "leads" / "models.py").read_text(
            encoding="utf-8"
        )
        block = source.split("class LeadProgramInterest(BaseModel):", 1)[1]
        block = block.split("class Meta:", 1)[0]
        self.assertNotIn("status = models.", block)
        self.assertNotIn("user_responded_at", block)

    def test_system_recommendations_are_disabled(self):
        source = (
            Path(settings.BASE_DIR) / "apps" / "leads" / "services" / "recommendations.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Automatic/system program suggestions are disabled", source)
