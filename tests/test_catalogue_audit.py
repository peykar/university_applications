from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicYear,
    Currency,
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
    University,
    UniversityType,
)


class CatalogueAuditCommandTests(TestCase):
    def setUp(self):
        country = Country.objects.create(iso2="TR", iso3="TUR", name_en="Türkiye")
        province = Province.objects.create(country=country, name_en="Istanbul")
        city = City.objects.create(province=province, name_en="Istanbul")
        self.university = University.objects.create(
            name_en="Audit University",
            name_fa="دانشگاه آزمون",
            name_tr="Denetim Üniversitesi",
            name_ar="جامعة التدقيق",
            description_en="Description",
            description_fa="توضیحات",
            description_tr="Aciklama",
            description_ar="وصف",
            website="https://example.com",
            city=city,
            university_type=UniversityType.PRIVATE,
        )
        self.language = ProgramLanguage.objects.create(
            name_en="English",
            name_fa="انگلیسی",
            name_tr="Ingilizce",
            name_ar="الإنجليزية",
        )
        self.year = AcademicYear.objects.create(name_en="2026-2027")
        self.intake = Intake.objects.create(
            university=self.university, academic_year=self.year, name_en="Academic Intake"
        )

    def _program_with_language(self):
        program = Program.objects.create(
            university=self.university,
            name_en="Computer Engineering",
            name_fa="مهندسی کامپیوتر",
            name_tr="Bilgisayar Mühendisliği",
            name_ar="هندسة الحاسوب",
            degree="bachelor",
            duration_months=48,
        )
        ProgramInstructionLanguage.objects.create(
            program=program, language=self.language, percentage=100, is_primary=True
        )
        return program

    def test_audit_reports_application_readiness_error_without_tuition(self):
        program = self._program_with_language()
        ProgramOffering.objects.create(program=program, academic_year=self.year, intake=self.intake)
        output = StringIO()

        call_command("audit_catalogue", stdout=output)

        self.assertIn("OFFERING_NO_TUITION", output.getvalue())

    def test_audit_json_is_machine_readable_and_clean_catalogue_has_no_errors(self):
        program = self._program_with_language()
        offering = ProgramOffering.objects.create(
            program=program, academic_year=self.year, intake=self.intake
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.TUITION,
            currency=Currency.USD,
            amount=5000,
            basis=FeeBasis.ANNUAL,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            call_command("audit_catalogue", json_output=path, stdout=StringIO())
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["summary"]["findings"]["ERROR"], 0)
        self.assertEqual(payload["summary"]["programs"], 1)
        self.assertEqual(payload["summary"]["offerings"], 1)

    def test_audit_detects_public_provenance_commentary(self):
        program = self._program_with_language()
        offering = ProgramOffering.objects.create(
            program=program,
            academic_year=self.year,
            intake=self.intake,
            notes="Imported from source workbook.",
        )
        OfferingFee.objects.create(
            offering=offering,
            fee_type=OfferingFeeType.TUITION,
            currency=Currency.USD,
            amount=5000,
            basis=FeeBasis.ANNUAL,
        )
        output = StringIO()

        call_command("audit_catalogue", stdout=output)

        self.assertIn("OFFERING_PUBLIC_PROVENANCE", output.getvalue())
