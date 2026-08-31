import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicUnit,
    OfferingFeeType,
    Program,
    ProgramOffering,
    University,
    UniversityCatalogueSource,
)


class UniversityProgramJsonImportTests(TestCase):
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
            name_en="JSON Import University",
            slug_en="json-import-university",
            created_by=self.user,
            updated_by=self.user,
        )
        self.other_university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Other University",
            slug_en="other-university-json-import",
            created_by=self.user,
            updated_by=self.user,
        )
        self.source = UniversityCatalogueSource.objects.create(
            university=self.university,
            title="2026 tuition sheet",
            received_at="2026-08-30",
            created_by=self.user,
            updated_by=self.user,
        )
        self.other_source = UniversityCatalogueSource.objects.create(
            university=self.other_university,
            title="Other tuition sheet",
            received_at="2026-08-30",
            created_by=self.user,
            updated_by=self.user,
        )

    def _payload(self):
        return {
            "schema_version": 2,
            "academic_units": [
                {
                    "slug_en": "faculty-of-engineering",
                    "name_en": "Faculty of Engineering",
                    "unit_type": "faculty",
                }
            ],
            "departments": [],
            "programs": [
                {
                    "slug_en": "software-engineering-english",
                    "name_en": "Software Engineering",
                    "degree": "bachelor",
                    "academic_unit": "faculty-of-engineering",
                    "department": None,
                    "study_mode": "on_campus",
                    "duration_months": 48,
                    "internal_notes": "Normalized from the university tuition sheet.",
                    "instruction_languages": [
                        {
                            "slug": "english",
                            "name_en": "English",
                            "percentage": "100",
                            "is_primary": True,
                        }
                    ],
                    "offerings": [
                        {
                            "academic_year": "2026-2027",
                            "intake": "Fall",
                            "fees": [
                                {
                                    "fee_type": "tuition",
                                    "currency": "USD",
                                    "amount": "18000.00",
                                    "basis": "annual",
                                },
                                {
                                    "fee_type": "discounted_tuition",
                                    "currency": "USD",
                                    "amount": "12000.00",
                                    "basis": "annual",
                                },
                                {
                                    "fee_type": "cash_payment",
                                    "currency": "USD",
                                    "amount": "11000.00",
                                    "basis": "annual",
                                },
                                {
                                    "fee_type": "deposit",
                                    "currency": "USD",
                                    "amount": "1000.00",
                                    "basis": "one_time",
                                },
                                {
                                    "fee_type": "preparatory",
                                    "currency": "USD",
                                    "amount": "3500.00",
                                    "basis": "annual",
                                },
                            ],
                            "preparation_included": False,
                            "notes": "Scholarship label preserved from source.",
                        }
                    ],
                }
            ],
        }

    def _write_payload(self, payload) -> Path:
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "programs.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _run(self, payload, *, source=None):
        call_command(
            "import_programs_for_university",
            str(self.university.pk),
            str((source or self.source).pk),
            str(self._write_payload(payload)),
        )

    def test_import_creates_program_academic_unit_languages_and_source_bound_offering(self):
        self._run(self._payload())

        unit = AcademicUnit.objects.get(
            university=self.university, slug_en="faculty-of-engineering"
        )
        program = Program.objects.get(
            university=self.university, slug_en="software-engineering-english"
        )
        offering = ProgramOffering.objects.get(program=program, source=self.source)

        self.assertEqual(program.academic_unit, unit)
        self.assertEqual(program.duration_months, 48)
        self.assertEqual(
            program.internal_notes,
            "Normalized from the university tuition sheet.",
        )
        self.assertEqual(program.instruction_language_display, "100% English")
        self.assertEqual(offering.fees.get(fee_type=OfferingFeeType.TUITION).amount, 18000)
        self.assertEqual(
            offering.fees.get(fee_type=OfferingFeeType.DISCOUNTED_TUITION).amount, 12000
        )
        self.assertEqual(offering.fees.get(fee_type=OfferingFeeType.CASH_PAYMENT).amount, 11000)
        self.assertEqual(offering.fees.get(fee_type=OfferingFeeType.DEPOSIT).amount, 1000)
        self.assertEqual(offering.fees.get(fee_type=OfferingFeeType.PREPARATORY).amount, 3500)
        self.assertEqual(offering.source, self.source)

    def test_reimport_updates_program_and_offering_without_duplicates(self):
        payload = self._payload()
        self._run(payload)
        payload["programs"][0]["name_en"] = "Software Engineering Updated"
        payload["programs"][0]["internal_notes"] = "Updated internal import note."
        payload["programs"][0]["offerings"][0]["fees"][0]["amount"] = "19000.00"
        self._run(payload)

        programs = Program.objects.filter(
            university=self.university, slug_en="software-engineering-english"
        )
        self.assertEqual(programs.count(), 1)
        program = programs.get()
        self.assertEqual(program.name_en, "Software Engineering Updated")
        self.assertEqual(program.internal_notes, "Updated internal import note.")
        offerings = ProgramOffering.objects.filter(program=program, source=self.source)
        self.assertEqual(offerings.count(), 1)
        self.assertEqual(offerings.get().fees.get(fee_type=OfferingFeeType.TUITION).amount, 19000)

    def test_reimport_without_internal_notes_preserves_existing_internal_notes(self):
        payload = self._payload()
        self._run(payload)

        payload["programs"][0].pop("internal_notes")
        payload["programs"][0]["name_en"] = "Software Engineering Renamed"
        self._run(payload)

        program = Program.objects.get(
            university=self.university, slug_en="software-engineering-english"
        )
        self.assertEqual(
            program.internal_notes,
            "Normalized from the university tuition sheet.",
        )

    def test_source_must_belong_to_university_before_any_import_writes(self):
        with self.assertRaises(CommandError):
            self._run(self._payload(), source=self.other_source)

        self.assertFalse(Program.objects.filter(university=self.university).exists())
        self.assertFalse(AcademicUnit.objects.filter(university=self.university).exists())

    def test_invalid_mixed_language_percentages_are_rejected_before_writes(self):
        payload = self._payload()
        payload["programs"][0]["instruction_languages"] = [
            {
                "slug": "english",
                "name_en": "English",
                "percentage": "30",
                "is_primary": True,
            },
            {
                "slug": "turkish",
                "name_en": "Turkish",
                "percentage": "60",
                "is_primary": False,
            },
        ]

        with self.assertRaises(CommandError):
            self._run(payload)

        self.assertFalse(Program.objects.filter(university=self.university).exists())
        self.assertFalse(AcademicUnit.objects.filter(university=self.university).exists())

    def test_import_accepts_native_unicode_localized_slugs(self):
        payload = self._payload()
        payload["academic_units"][0].update(
            {
                "slug_fa": "دانشکده-مهندسی",
                "slug_tr": "mühendislik-fakültesi",
                "slug_ar": "كلية-الهندسة",
            }
        )
        payload["programs"][0].update(
            {
                "name_fa": "مهندسی نرم‌افزار",
                "name_tr": "Yazılım Mühendisliği",  # noqa: RUF001 -- intentional Turkish dotless i
                "name_ar": "هندسة البرمجيات",
                "slug_fa": "مهندسی-نرمافزار",
                "slug_tr": "yazılım-mühendisliği",  # noqa: RUF001 -- intentional Turkish dotless i
                "slug_ar": "هندسة-البرمجيات",
            }
        )

        self._run(payload)

        program = Program.objects.get(
            university=self.university, slug_en="software-engineering-english"
        )
        self.assertEqual(program.slug_fa, "مهندسی-نرمافزار")
        self.assertEqual(program.slug_tr, "yazılım-mühendisliği")  # noqa: RUF001 -- intentional Turkish dotless i
        self.assertEqual(program.slug_ar, "هندسة-البرمجيات")

    def test_program_slugs_must_be_unique_inside_file(self):
        payload = self._payload()
        payload["programs"].append(dict(payload["programs"][0]))

        with self.assertRaises(CommandError):
            self._run(payload)

    def test_program_internal_notes_must_be_text_or_null(self):
        payload = self._payload()
        payload["programs"][0]["internal_notes"] = {"unexpected": "object"}

        with self.assertRaises(CommandError):
            self._run(payload)

        self.assertFalse(Program.objects.filter(university=self.university).exists())
