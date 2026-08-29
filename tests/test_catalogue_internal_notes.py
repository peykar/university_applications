from pathlib import Path

from django.test import SimpleTestCase

from apps.api.serializers import ProgramSerializer


class ProgramInternalNotesVisibilityTests(SimpleTestCase):
    def test_program_api_does_not_expose_internal_notes(self):
        self.assertNotIn("internal_notes", ProgramSerializer.Meta.fields)

    def test_public_and_customer_templates_do_not_reference_internal_notes(self):
        roots = (Path("templates/public"), Path("templates/leads"))
        referenced_by = []
        for root in roots:
            if not root.exists():
                continue
            for template in root.rglob("*.html"):
                if "internal_notes" in template.read_text(encoding="utf-8"):
                    referenced_by.append(str(template))

        self.assertEqual(referenced_by, [])
