from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.public.services.program_filters import ProgramFilterState, apply_program_filters
from apps.universities.management.commands.import_rasa_catalogue import (
    as_duration_months,
    parse_instruction_languages,
)
from apps.universities.models import (
    AcademicUnit,
    AcademicUnitType,
    AcademicYear,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
    Semester,
    StudyMode,
    University,
    UniversityCatalogueSource,
)


class CatalogueV2Tests(TestCase):
    def setUp(self):
        self.user = get_system_user()
        country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            slug_en="turkiye",
            created_by=self.user,
            updated_by=self.user,
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            slug_en="istanbul",
            created_by=self.user,
            updated_by=self.user,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            slug_en="istanbul",
            created_by=self.user,
            updated_by=self.user,
        )
        self.university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Catalogue University",
            slug_en="catalogue-university",
            created_by=self.user,
            updated_by=self.user,
        )
        self.other_university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Other University",
            slug_en="other-university",
            created_by=self.user,
            updated_by=self.user,
        )
        self.english = ProgramLanguage.objects.create(
            name_en="English",
            slug_en="english",
            created_by=self.user,
            updated_by=self.user,
        )
        self.turkish = ProgramLanguage.objects.create(
            name_en="Turkish",
            slug_en="turkish",
            created_by=self.user,
            updated_by=self.user,
        )
        self.unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type=AcademicUnitType.FACULTY,
            name_en="Faculty of Engineering",
            slug_en="faculty-engineering",
            created_by=self.user,
            updated_by=self.user,
        )
        self.program = Program.objects.create(
            university=self.university,
            academic_unit=self.unit,
            program_language=self.english,
            study_mode=StudyMode.HYBRID,
            duration_months=18,
            degree="master",
            name_en="Data Engineering",
            slug_en="data-engineering",
            created_by=self.user,
            updated_by=self.user,
        )
        self.year = AcademicYear.objects.create(
            name_en="2026-2027", created_by=self.user, updated_by=self.user
        )
        self.semester = Semester.objects.create(
            name_en="Fall", created_by=self.user, updated_by=self.user
        )

    def test_import_helpers_preserve_fractional_duration_and_mixed_languages(self):
        self.assertEqual(as_duration_months("1.5"), 18)
        self.assertEqual(
            parse_instruction_languages("30% English & 70% Turkish"),
            [("English", Decimal("30")), ("Turkish", Decimal("70"))],
        )

    def test_instruction_language_percentage_is_bounded(self):
        row = ProgramInstructionLanguage(
            program=self.program,
            language=self.turkish,
            percentage=Decimal("101"),
        )
        with self.assertRaises(ValidationError):
            row.full_clean()

    def test_academic_unit_must_belong_to_program_university(self):
        other_unit = AcademicUnit.objects.create(
            university=self.other_university,
            unit_type=AcademicUnitType.SCHOOL,
            name_en="Other School",
            slug_en="other-school",
            created_by=self.user,
            updated_by=self.user,
        )
        self.program.academic_unit = other_unit
        with self.assertRaises(ValidationError):
            self.program.full_clean()

    def test_mixed_languages_and_fractional_duration_are_canonical(self):
        ProgramInstructionLanguage.objects.filter(program=self.program).delete()
        ProgramInstructionLanguage.objects.create(
            program=self.program,
            language=self.english,
            percentage=Decimal("30"),
            is_primary=True,
        )
        ProgramInstructionLanguage.objects.create(
            program=self.program,
            language=self.turkish,
            percentage=Decimal("70"),
        )

        self.assertEqual(self.program.duration_display, "1.5 years")
        self.assertEqual(
            self.program.instruction_language_display,
            "30% English · 70% Turkish",
        )

    def test_language_filter_matches_any_canonical_instruction_language(self):
        ProgramInstructionLanguage.objects.create(
            program=self.program,
            language=self.turkish,
        )
        result = apply_program_filters(
            Program.objects.all(),
            ProgramFilterState(language="turkish", study_mode=StudyMode.HYBRID),
        )
        self.assertEqual(list(result), [self.program])

    def test_source_and_offering_keep_pricing_semantics_and_provenance(self):
        source = UniversityCatalogueSource.objects.create(
            university=self.university,
            title="2026-2027 agent tuition sheet",
            received_at=date(2026, 8, 29),
            academic_year=self.year,
            recorded_by=self.user,
            created_by=self.user,
            updated_by=self.user,
        )
        offering = ProgramOffering.objects.create(
            program=self.program,
            academic_year=self.year,
            semester=self.semester,
            fee_basis="annual",
            currency="USD",
            tuition=Decimal("18000"),
            tuition_discounted=Decimal("11000"),
            tuition_cash=Decimal("10000"),
            deposit=Decimal("1000"),
            preparatory_tuition=Decimal("3950"),
            preparation_included=False,
            notes="Scholarship label preserved from source sheet.",
            valid_from=date(2026, 8, 1),
            valid_until=date(2026, 12, 31),
            source=source,
            created_by=self.user,
            updated_by=self.user,
        )

        self.assertEqual(offering.tuition, Decimal("18000"))
        self.assertEqual(offering.tuition_discounted, Decimal("11000"))
        self.assertEqual(offering.tuition_cash, Decimal("10000"))
        self.assertEqual(offering.deposit, Decimal("1000"))
        self.assertEqual(offering.preparatory_tuition, Decimal("3950"))
        self.assertEqual(offering.source, source)

    def test_offering_rejects_source_from_other_university(self):
        source = UniversityCatalogueSource.objects.create(
            university=self.other_university,
            title="Wrong source",
            received_at=date(2026, 8, 29),
            created_by=self.user,
            updated_by=self.user,
        )
        offering = ProgramOffering(
            program=self.program,
            academic_year=self.year,
            semester=self.semester,
            fee_basis="annual",
            currency="USD",
            tuition=Decimal("5000"),
            source=source,
        )
        with self.assertRaises(ValidationError):
            offering.full_clean()

    def test_legacy_fields_backfill_without_losing_meaning(self):
        legacy = Program.objects.create(
            university=self.university,
            program_language=self.turkish,
            duration=4,
            degree="bachelor",
            name_en="Legacy Program",
            slug_en="legacy-program",
            created_by=self.user,
            updated_by=self.user,
        )
        Program.objects.filter(pk=legacy.pk).update(duration_months=None)
        ProgramInstructionLanguage.objects.filter(program=legacy).delete()

        call_command("backfill_catalogue_v2")
        legacy.refresh_from_db()

        self.assertEqual(legacy.duration, 4)
        self.assertEqual(legacy.duration_months, 48)
        self.assertTrue(legacy.instruction_language_rows.filter(language=self.turkish).exists())
