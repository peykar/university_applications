from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.content.models import FAQCategory
from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import Program, University


class RebuildSlugsCommandTests(TestCase):
    def setUp(self):
        self.actor = get_system_user()
        self.country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            name_fa="ترکیه",
            slug_en="old-country",
            slug_fa="old-fa",
            created_by=self.actor,
            updated_by=self.actor,
        )
        province = Province.objects.create(
            country=self.country,
            name_en="Istanbul",
            created_by=self.actor,
            updated_by=self.actor,
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self.university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Istanbul Medipol University",
            name_fa="دانشگاه مدیپول استانبول",
            slug_en="old-university",
            slug_fa="old-university-fa",
            created_by=self.actor,
            updated_by=self.actor,
        )

    def test_rebuild_replaces_stale_slugs_from_current_names(self):
        Program.objects.create(
            university=self.university,
            name_en="Software Engineering",
            name_tr="Yazılım Mühendisliği",  # noqa: RUF001 -- intentional Turkish dotless i
            slug_en="legacy-program",
            slug_tr="legacy-program-tr",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )

        call_command("rebuild_slugs", stdout=StringIO())

        self.university.refresh_from_db()
        program = Program.objects.get(name_en="Software Engineering")
        self.assertEqual(self.university.slug_en, "istanbul-medipol-university")
        self.assertEqual(self.university.slug_fa, "دانشگاه-مدیپول-استانبول")
        self.assertEqual(program.slug_en, "software-engineering")
        self.assertEqual(program.slug_tr, "yazılım-mühendisliği")  # noqa: RUF001

    def test_dry_run_reports_but_does_not_write(self):
        output = StringIO()

        call_command("rebuild_slugs", dry_run=True, stdout=output)

        self.university.refresh_from_db()
        self.assertEqual(self.university.slug_en, "old-university")
        self.assertIn("would change", output.getvalue())

    def test_collision_aborts_before_any_write(self):
        FAQCategory.objects.create(name_en="Admissions", key="first")
        FAQCategory.objects.create(name_en="Admissions", key="second")

        with self.assertRaisesMessage(CommandError, "generated values collide"):
            call_command("rebuild_slugs", stdout=StringIO())

        self.university.refresh_from_db()
        self.assertEqual(self.university.slug_en, "old-university")
        self.assertEqual(
            set(FAQCategory.objects.values_list("key", flat=True)),
            {"first", "second"},
        )

    def test_blank_localized_name_does_not_clear_existing_slug(self):
        self.university.name_ar = ""
        self.university.slug_ar = "keep-existing-ar"
        self.university.save(update_fields={"name_ar", "slug_ar"})

        call_command("rebuild_slugs", stdout=StringIO())

        self.university.refresh_from_db()
        self.assertEqual(self.university.slug_ar, "keep-existing-ar")
