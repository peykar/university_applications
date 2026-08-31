from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import Program, University


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

    def test_command_adds_thesis_type_to_graduate_slug(self):
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
