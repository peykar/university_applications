import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicUnit,
    AcademicYear,
    Department,
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
    University,
    UniversityCatalogueSource,
)


class UniversityDataDumpTests(TestCase):
    def setUp(self):
        self.user = get_system_user()
        country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            name_tr="Türkiye",
            slug_en="turkiye",
            slug_tr="turkiye",
            created_by=self.user,
            updated_by=self.user,
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            name_tr="İstanbul",
            slug_en="istanbul",
            slug_tr="istanbul",
            created_by=self.user,
            updated_by=self.user,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            name_tr="İstanbul",
            slug_en="istanbul",
            slug_tr="istanbul",
            created_by=self.user,
            updated_by=self.user,
        )
        self.university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Rasa Text University",
            name_fa="دانشگاه راسا",
            name_tr="Rasa Üniversitesi",
            slug_en="rasa-text-university",
            description_en="English university description",
            description_fa="توضیحات دانشگاه",
            created_by=self.user,
            updated_by=self.user,
        )
        unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type="faculty",
            name_en="Faculty of Health Sciences",
            name_tr="Sağlık Bilimleri Fakültesi",  # noqa: RUF001
            slug_en="faculty-of-health-sciences",
            description_en="English faculty description",
            created_by=self.user,
            updated_by=self.user,
        )
        department = Department.objects.create(
            university=self.university,
            name_en="Audiology",
            name_fa="شنوایی شناسی",
            slug_en="audiology",
            description_en="Department description",
            created_by=self.user,
            updated_by=self.user,
        )
        language = ProgramLanguage.objects.create(
            name_en="Turkish",
            name_tr="Türkçe",
            slug_en="turkish",
            created_by=self.user,
            updated_by=self.user,
        )
        academic_year = AcademicYear.objects.create(
            name_en="2026-2027", created_by=self.user, updated_by=self.user
        )
        intake = Intake.objects.create(
            university=self.university,
            academic_year=academic_year,
            name_en="Fall",
            name_tr="Güz",
            created_by=self.user,
            updated_by=self.user,
        )
        source = UniversityCatalogueSource.objects.create(
            university=self.university,
            title="Rasa import",
            received_at="2026-08-30",
            notes="Source note",
            created_by=self.user,
            updated_by=self.user,
        )
        program = Program.objects.create(
            university=self.university,
            academic_unit=unit,
            department=department,
            name_en="Audiology",
            name_fa="شنوایی شناسی",
            name_tr="Odyoloji",
            slug_en="audiology-turkish",
            description_en="English programme description",
            description_fa="توضیحات برنامه",
            description_tr="Program açıklaması",  # noqa: RUF001
            internal_notes="Internal Rasa mapping note",
            degree="bachelor",
            duration_months=48,
            created_by=self.user,
            updated_by=self.user,
        )
        ProgramInstructionLanguage.objects.create(
            program=program,
            language=language,
            percentage=100,
            is_primary=True,
            created_by=self.user,
            updated_by=self.user,
        )
        offering = ProgramOffering.objects.create(
            program=program,
            academic_year=academic_year,
            intake=intake,
            notes="Offering note",
            source=source,
            created_by=self.user,
            updated_by=self.user,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.TUITION,
            currency="USD",
            amount="6500.00",
            basis=FeeBasis.ANNUAL,
            created_by=self.user,
            updated_by=self.user,
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.CASH_PAYMENT,
            currency="USD",
            amount="5850.00",
            basis=FeeBasis.ANNUAL,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_dump_contains_localized_catalogue_data_and_related_offerings(self):
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "university.json"
            stdout = StringIO()
            call_command(
                "dump_university_data",
                str(self.university.pk),
                output=str(output),
                stdout=stdout,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["scope"], "university_catalogue")
        self.assertEqual(payload["university"]["name_fa"], "دانشگاه راسا")
        self.assertEqual(payload["university"]["city"]["province"]["country"]["iso2"], "TR")
        self.assertEqual(len(payload["academic_units"]), 1)
        self.assertEqual(len(payload["departments"]), 1)
        self.assertEqual(len(payload["catalogue_sources"]), 1)
        self.assertEqual(len(payload["programs"]), 1)
        program = payload["programs"][0]
        self.assertEqual(program["name_tr"], "Odyoloji")
        self.assertEqual(program["description_fa"], "توضیحات برنامه")
        self.assertEqual(program["internal_notes"], "Internal Rasa mapping note")
        self.assertEqual(program["instruction_languages"][0]["language"]["name_tr"], "Türkçe")
        fee_amounts = {fee["fee_type"]: fee["amount"] for fee in program["offerings"][0]["fees"]}
        self.assertEqual(fee_amounts["tuition"], "6500.00")
        self.assertEqual(fee_amounts["cash_payment"], "5850.00")
        self.assertEqual(program["offerings"][0]["source"]["title"], "Rasa import")
        self.assertIn("Programs=1", stdout.getvalue())
        self.assertIn(str(output), stdout.getvalue())

    def test_default_output_filename_uses_university_id(self):
        with TemporaryDirectory() as temp_dir:
            old_cwd = Path.cwd()
            try:
                import os

                os.chdir(temp_dir)
                call_command("dump_university_data", str(self.university.pk))
                expected = Path(temp_dir) / f"university_{self.university.pk}_catalogue.json"
                self.assertTrue(expected.exists())
            finally:
                os.chdir(old_cwd)

    def test_unknown_university_is_rejected_without_creating_output(self):
        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "missing.json"
            with self.assertRaises(CommandError):
                call_command(
                    "dump_university_data",
                    "00000000-0000-0000-0000-000000000000",
                    output=str(output),
                )
            self.assertFalse(output.exists())
