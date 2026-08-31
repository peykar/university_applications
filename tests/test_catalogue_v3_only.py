from pathlib import Path

from django.core.exceptions import FieldDoesNotExist
from django.test import SimpleTestCase

from apps.universities.models import Program, ProgramOffering

ROOT = Path(__file__).resolve().parents[1]


class CatalogueV3OnlyContractTests(SimpleTestCase):
    def test_legacy_program_fields_are_removed(self):
        for field_name in ("program_language", "duration"):
            with self.assertRaises(FieldDoesNotExist):
                Program._meta.get_field(field_name)

    def test_legacy_offering_fields_are_removed(self):
        for field_name in (
            "semester",
            "fee_basis",
            "currency",
            "tuition",
            "tuition_discount_percentage",
            "tuition_discounted",
            "cash_discount_percentage",
            "tuition_cash",
            "tuition_annual_installment",
            "deposit",
            "preparatory_tuition",
        ):
            with self.assertRaises(FieldDoesNotExist):
                ProgramOffering._meta.get_field(field_name)

    def test_templates_do_not_use_removed_offering_fee_basis_accessor(self):
        for relative_path in (
            "templates/leads/lead_detail.html",
            "templates/leads/lead_section.html",
        ):
            source = (ROOT / relative_path).read_text()
            self.assertNotIn("offering.get_fee_basis_display", source)
            self.assertNotIn("program_offering.get_fee_basis_display", source)

    def test_removed_backfill_command_is_not_present(self):
        self.assertFalse(
            (ROOT / "apps/universities/management/commands/backfill_catalogue_v2.py").exists()
        )

    def test_cutover_command_does_not_reintroduce_legacy_models(self):
        source = (
            ROOT / "apps/universities/management/commands/prepare_catalogue_v3_cutover.py"
        ).read_text()
        self.assertNotIn("from apps.universities.models import Semester", source)
        self.assertIn("connection.introspection", source)
        self.assertIn("OfferingFee", source)
        self.assertIn("Intake", source)
