from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicUnit,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    University,
)


class RebuildProgramSlugsCommandTests(TestCase):
    def setUp(self):
        actor = get_system_user()
        country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            slug_en="turkiye",
            created_by=actor,
            updated_by=actor,
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            slug_en="istanbul",
            created_by=actor,
            updated_by=actor,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            slug_en="istanbul",
            created_by=actor,
            updated_by=actor,
        )
        self.university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Istanbul Atlas University",
            slug_en="istanbul-atlas-university",
            created_by=actor,
            updated_by=actor,
        )
        self.program = Program.objects.create(
            university=self.university,
            name_en="Nursing",
            slug_en="nursing-bachelor-turkish",
            degree="bachelor",
            created_by=actor,
            updated_by=actor,
        )
        self.turkish = ProgramLanguage.objects.create(
            name_en="Turkish",
            slug_en="turkish",
            created_by=actor,
            updated_by=actor,
        )
        ProgramInstructionLanguage.objects.create(
            program=self.program,
            language=self.turkish,
            is_primary=True,
            created_by=actor,
            updated_by=actor,
        )
        # Simulate a pre-change database row without going through Program.save().
        Program.objects.filter(pk=self.program.pk).update(slug_en="nursing-bachelor-turkish")

    def test_command_rebuilds_existing_slug(self):
        call_command("rebuild_program_slugs", stdout=StringIO())
        self.program.refresh_from_db()
        self.assertEqual(self.program.slug_en, "istanbul-atlas-university-nursing-bachelor-turkish")

    def test_dry_run_does_not_write(self):
        call_command("rebuild_program_slugs", "--dry-run", stdout=StringIO())
        self.program.refresh_from_db()
        self.assertEqual(self.program.slug_en, "nursing-bachelor-turkish")

    def test_command_adds_academic_unit_to_existing_slug(self):
        unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type="faculty",
            name_en="Faculty of Health Sciences",
            slug_en="faculty-of-health-sciences",
            created_by=get_system_user(),
            updated_by=get_system_user(),
        )
        Program.objects.filter(pk=self.program.pk).update(academic_unit=unit)
        call_command("rebuild_program_slugs", stdout=StringIO())
        self.program.refresh_from_db()
        self.assertEqual(
            self.program.slug_en,
            "istanbul-atlas-university-faculty-of-health-sciences-nursing-bachelor-turkish",
        )

    def test_command_preserves_untranslated_hierarchy_with_english_fallback(self):
        unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type="vocational_school",
            name_en="Vocational School of Health Services",
            slug_en="vocational-school-of-health-services",
            created_by=get_system_user(),
            updated_by=get_system_user(),
        )
        self.university.name_fa = "مدیپول استانبول"
        self.university.slug_fa = "مدیپول-استانبول"
        self.university.save()
        self.program.name_fa = "مدیریت موسسات درمانی"
        self.program.save()
        self.turkish.name_fa = "ترکی"
        self.turkish.slug_fa = "ترکی"
        self.turkish.save()
        Program.objects.filter(pk=self.program.pk).update(
            academic_unit=unit,
            slug_fa="مدیپول-استانبول-مدیریت-موسسات-درمانی-کارشناسی-ترکی",
        )
        call_command("rebuild_program_slugs", stdout=StringIO())
        self.program.refresh_from_db()
        self.assertEqual(
            self.program.slug_fa,
            "مدیپول-استانبول-vocational-school-of-health-services-"
            "مدیریت-موسسات-درمانی-کارشناسی-ترکی",
        )

    def test_command_adds_thesis_type_to_graduate_slug(self):
        self.program.name_en = "Business Administration"
        self.program.degree = "master"
        self.program.thesis_type = "non_thesis"
        self.program.save()
        Program.objects.filter(pk=self.program.pk).update(
            slug_en="istanbul-atlas-university-business-administration-master-turkish"
        )
        call_command("rebuild_program_slugs", stdout=StringIO())
        self.program.refresh_from_db()
        self.assertEqual(
            self.program.slug_en,
            "istanbul-atlas-university-business-administration-master-non-thesis-turkish",
        )

    def test_command_reports_and_skips_conflicting_programs_but_updates_others(self):
        actor = get_system_user()
        conflicting = Program.objects.create(
            university=self.university,
            name_en="Temporary Combined Nursing",
            slug_en="temporary-combined-nursing",
            degree="bachelor",
            created_by=actor,
            updated_by=actor,
        )
        ProgramInstructionLanguage.objects.create(
            program=conflicting,
            language=self.turkish,
            is_primary=True,
            created_by=actor,
            updated_by=actor,
        )
        Program.objects.filter(pk=conflicting.pk).update(
            name_en="Nursing",
            slug_en="legacy-conflicting-nursing",
        )

        safe = Program.objects.create(
            university=self.university,
            name_en="Physiotherapy",
            slug_en="physiotherapy-bachelor-turkish",
            degree="bachelor",
            created_by=actor,
            updated_by=actor,
        )
        ProgramInstructionLanguage.objects.create(
            program=safe,
            language=self.turkish,
            is_primary=True,
            created_by=actor,
            updated_by=actor,
        )
        Program.objects.filter(pk=safe.pk).update(slug_en="physiotherapy-bachelor-turkish")

        stdout = StringIO()
        call_command("rebuild_program_slugs", stdout=stdout)

        self.program.refresh_from_db()
        conflicting.refresh_from_db()
        safe.refresh_from_db()
        expected_conflict = "istanbul-atlas-university-nursing-bachelor-turkish"
        self.assertEqual(self.program.slug_en, "nursing-bachelor-turkish")
        self.assertEqual(conflicting.slug_en, "legacy-conflicting-nursing")
        self.assertEqual(
            safe.slug_en,
            "istanbul-atlas-university-physiotherapy-bachelor-turkish",
        )
        output = stdout.getvalue()
        self.assertIn(f"CONFLICT slug_en='{expected_conflict}'", output)
        self.assertIn(str(self.program.pk), output)
        self.assertIn(str(conflicting.pk), output)
        self.assertIn("conflicts=1, skipped_programs=2", output)
