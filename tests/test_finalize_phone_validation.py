from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.phone import normalize_phone_number


class FinalizePhoneValidationTests(SimpleTestCase):
    def test_phone_normalizer_converts_parse_error_to_value_error(self):
        with self.assertRaises(ValueError):
            normalize_phone_number("0612345678")

    def test_finalization_validates_phone_before_student_creation(self):
        root = Path(settings.BASE_DIR)
        conversion = (root / "apps/leads/services/conversion.py").read_text(encoding="utf-8")
        self.assertIn("student.full_clean(", conversion)
        self.assertLess(
            conversion.index("student.full_clean("),
            conversion.index("student.save()"),
        )
