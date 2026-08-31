from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse

from apps.content.models import FAQCategory
from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import (
    AcademicUnit,
    Department,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    University,
)


class UnicodeCatalogueSlugRoutingTests(SimpleTestCase):
    unicode_program_slug = "birûni-üniversite-dentistry-turkish"
    unicode_university_slug = "birûni-üniversite"

    def test_public_program_detail_reverse_accepts_persisted_unicode_slug(self):
        url = reverse("program-detail", args=[self.unicode_program_slug])

        self.assertIn("bir%C3%BBni-%C3%BCniversite-dentistry-turkish", url)

    def test_apply_program_reverse_accepts_persisted_unicode_slug(self):
        url = reverse("apply-program", args=[self.unicode_program_slug])

        self.assertIn("bir%C3%BBni-%C3%BCniversite-dentistry-turkish", url)

    def test_public_university_detail_reverse_accepts_persisted_unicode_slug(self):
        url = reverse("university-detail", args=[self.unicode_university_slug])

        self.assertIn("bir%C3%BBni-%C3%BCniversite", url)

    def test_api_program_pattern_accepts_unicode_slug(self):
        match = resolve(
            f"/programs/{self.unicode_program_slug}/",
            urlconf="apps.api.urls",
        )

        self.assertEqual(match.kwargs["slug"], self.unicode_program_slug)

    def test_api_university_pattern_accepts_unicode_slug(self):
        match = resolve(
            f"/universities/{self.unicode_university_slug}/",
            urlconf="apps.api.urls",
        )

        self.assertEqual(match.kwargs["slug"], self.unicode_university_slug)


class UnicodeLocalizedCatalogueSlugValidationTests(TestCase):
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
        self.city = City.objects.create(
            province=province,
            name_en="Istanbul",
            slug_en="istanbul",
            created_by=actor,
            updated_by=actor,
        )
        self.actor = actor

    def test_university_accepts_unicode_localized_slugs(self):
        university = University(
            city=self.city,
            university_type="private",
            name_en="Istanbul Medipol",
            name_fa="مدیپول استانبول",
            name_tr="İstanbul Medipol Üniversitesi",
            name_ar="جامعة إسطنبول ميديبول",
            slug_en="istanbul-medipol",
            slug_fa="مدیپول-استانبول",
            slug_tr="istanbul-medipol-üniversitesi",
            slug_ar="جامعة-إسطنبول-ميديبول",
            created_by=self.actor,
            updated_by=self.actor,
        )

        try:
            university.full_clean()
        except ValidationError as exc:  # pragma: no cover - failure detail
            self.fail(f"Unicode localized University slugs were rejected: {exc}")

    def test_program_accepts_unicode_localized_slugs_while_english_stays_ascii(self):
        university = University.objects.create(
            city=self.city,
            university_type="private",
            name_en="Istanbul Medipol",
            slug_en="istanbul-medipol",
            created_by=self.actor,
            updated_by=self.actor,
        )
        program = Program(
            university=university,
            name_en="Medicine",
            name_fa="پزشکی",
            name_tr="Tıp",  # noqa: RUF001 -- intentional Turkish dotless i
            name_ar="الطب",
            slug_en="medicine",
            slug_fa="پزشکی",
            slug_tr="tıp",  # noqa: RUF001 -- intentional Turkish dotless i
            slug_ar="الطب",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )

        try:
            program.full_clean()
        except ValidationError as exc:  # pragma: no cover - failure detail
            self.fail(f"Unicode localized Program slugs were rejected: {exc}")

        program.slug_en = "پزشکی"
        with self.assertRaises(ValidationError):
            program.full_clean()

    def test_localized_slug_fields_enable_unicode_and_english_does_not(self):
        for model in (University, Program, Country, Province, City):
            self.assertFalse(model._meta.get_field("slug_en").allow_unicode)
            for field_name in ("slug_fa", "slug_tr", "slug_ar"):
                self.assertTrue(model._meta.get_field(field_name).allow_unicode)


class LocalizedSlugAutogenerationTests(TestCase):
    def setUp(self):
        self.actor = get_system_user()
        self.country = Country.objects.create(
            iso2="TR",
            iso3="TUR",
            name_en="Türkiye",
            name_fa="ترکیه",
            name_tr="Türkiye",
            name_ar="تركيا",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self.province = Province.objects.create(
            country=self.country,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self.city = City.objects.create(
            province=self.province,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            created_by=self.actor,
            updated_by=self.actor,
        )

    def test_shared_localized_slug_fields_are_optional_in_admin_forms(self):
        for model in (University, Program, Country, Province, City):
            for field_name in ("slug_en", "slug_fa", "slug_tr", "slug_ar"):
                self.assertTrue(model._meta.get_field(field_name).blank)
        self.assertTrue(FAQCategory._meta.get_field("key").blank)

    def test_save_generates_missing_slugs_from_matching_localized_names(self):
        university = University.objects.create(
            city=self.city,
            university_type="private",
            name_en="Istanbul Medipol University",
            name_fa="دانشگاه مدیپول استانبول",
            name_tr="İstanbul Medipol Üniversitesi",
            name_ar="جامعة إسطنبول ميديبول",
            created_by=self.actor,
            updated_by=self.actor,
        )

        self.assertEqual(university.slug_en, "istanbul-medipol-university")
        self.assertEqual(university.slug_fa, "دانشگاه-مدیپول-استانبول")
        self.assertEqual(university.slug_tr, "istanbul-medipol-üniversitesi")
        self.assertEqual(university.slug_ar, "جامعة-إسطنبول-ميديبول")

    def test_geography_models_use_the_same_slug_generation_contract(self):
        self.assertEqual(self.country.slug_en, "turkiye")
        self.assertEqual(self.country.slug_fa, "ترکیه")
        self.assertEqual(self.country.slug_tr, "türkiye")
        self.assertEqual(self.country.slug_ar, "تركيا")
        self.assertEqual(self.province.slug_fa, "استانبول")
        self.assertEqual(self.city.slug_ar, "إسطنبول")

    def test_program_rebuilds_native_unicode_slugs_from_structured_fields(self):
        university = University.objects.create(
            city=self.city,
            university_type="private",
            name_en="Istanbul Medipol",
            name_fa="مدیپول استانبول",
            name_tr="İstanbul Medipol",
            name_ar="ميديبول إسطنبول",
            created_by=self.actor,
            updated_by=self.actor,
        )
        program = Program.objects.create(
            university=university,
            name_en="Medicine",
            name_fa="پزشکی",
            name_tr="Tıp",  # noqa: RUF001 -- intentional Turkish dotless i
            name_ar="الطب",
            slug_en="medicine-custom",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )

        self.assertEqual(program.slug_en, "istanbul-medipol-medicine-bachelor")
        self.assertEqual(program.slug_fa, "مدیپول-استانبول-پزشکی-کارشناسی")
        self.assertEqual(
            program.slug_tr,
            "istanbul-medipol-tıp-lisans",  # noqa: RUF001 -- intentional Turkish dotless i
        )
        self.assertEqual(program.slug_ar, "ميديبول-إسطنبول-الطب-بكالوريوس")

        program.name_en = "Medicine Updated"
        program.save()
        self.assertEqual(program.slug_en, "istanbul-medipol-medicine-updated-bachelor")

    def test_non_catalogue_slug_field_uses_related_name_when_blank(self):
        category = FAQCategory.objects.create(
            name_en="Admissions and Applications",
            created_by=self.actor,
            updated_by=self.actor,
        )

        self.assertEqual(category.key, "admissions-and-applications")

    def test_full_clean_populates_slugs_before_admin_save(self):
        university = University(
            city=self.city,
            university_type="private",
            name_en="Medipol Test University",
            name_fa="دانشگاه آزمایشی مدیپول",
            created_by=self.actor,
            updated_by=self.actor,
        )

        university.full_clean()

        self.assertEqual(university.slug_en, "medipol-test-university")
        self.assertEqual(university.slug_fa, "دانشگاه-آزمایشی-مدیپول")
        self.assertEqual(university.slug_tr, "")
        self.assertEqual(university.slug_ar, "")


class ProgramCanonicalPublicSlugTests(TestCase):
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
        self.actor = actor
        self.university = University.objects.create(
            city=city,
            university_type="private",
            name_en="Istanbul Atlas University",
            name_tr="İstanbul Atlas Üniversitesi",
            slug_en="istanbul-atlas-university",
            slug_tr="istanbul-atlas-üniversitesi",
            created_by=actor,
            updated_by=actor,
        )
        self.english = ProgramLanguage.objects.create(
            name_en="English",
            name_tr="İngilizce",
            slug_en="english",
            slug_tr="ingilizce",
            created_by=actor,
            updated_by=actor,
        )
        self.turkish = ProgramLanguage.objects.create(
            name_en="Turkish",
            name_tr="Türkçe",
            slug_en="turkish",
            slug_tr="türkçe",
            created_by=actor,
            updated_by=actor,
        )

    def _add_language(self, program, language, *, primary=True):
        ProgramInstructionLanguage.objects.create(
            program=program,
            language=language,
            is_primary=primary,
            created_by=self.actor,
            updated_by=self.actor,
        )
        program.refresh_from_db()

    def test_program_slug_is_derived_from_structured_fields(self):
        program = Program.objects.create(
            university=self.university,
            name_en="Nursing",
            name_tr="Hemşirelik",
            slug_en="legacy-custom-slug",
            slug_tr="eski-özel-slug",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.turkish)
        self.assertEqual(
            program.slug_en,
            "istanbul-atlas-university-nursing-bachelor-turkish",
        )
        self.assertEqual(
            program.slug_tr,
            "istanbul-atlas-üniversitesi-hemşirelik-lisans-türkçe",
        )

    def test_hierarchy_slug_falls_back_to_english_when_locale_is_missing(self):
        academic_unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type="vocational_school",
            name_en="Vocational School of Health Services",
            slug_en="vocational-school-of-health-services",
            created_by=self.actor,
            updated_by=self.actor,
        )
        department = Department.objects.create(
            university=self.university,
            name_en="Department of Health Management",
            slug_en="department-of-health-management",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self.university.name_fa = "مدیپول استانبول"
        self.university.slug_fa = "مدیپول-استانبول"
        self.university.save()
        self.turkish.name_fa = "ترکی"
        self.turkish.slug_fa = "ترکی"
        self.turkish.save()
        program = Program.objects.create(
            university=self.university,
            academic_unit=academic_unit,
            department=department,
            name_en="Management of Health Institutions",
            name_fa="مدیریت موسسات درمانی",
            degree="associate",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.turkish)
        self.assertEqual(
            program.slug_fa,
            "مدیپول-استانبول-vocational-school-of-health-services-"
            "department-of-health-management-مدیریت-موسسات-درمانی-کاردانی-ترکی",
        )

    def test_program_slug_includes_academic_unit_and_department_when_present(self):
        academic_unit = AcademicUnit.objects.create(
            university=self.university,
            unit_type="faculty",
            name_en="Faculty of Engineering",
            slug_en="faculty-of-engineering",
            created_by=self.actor,
            updated_by=self.actor,
        )
        department = Department.objects.create(
            university=self.university,
            name_en="Department of Software Engineering",
            slug_en="department-of-software-engineering",
            created_by=self.actor,
            updated_by=self.actor,
        )
        program = Program.objects.create(
            university=self.university,
            academic_unit=academic_unit,
            department=department,
            name_en="Software Engineering",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.english)
        self.assertEqual(
            program.slug_en,
            "istanbul-atlas-university-faculty-of-engineering-"
            "department-of-software-engineering-software-engineering-bachelor-english",
        )

    def test_graduate_program_slug_includes_thesis_type(self):
        program = Program.objects.create(
            university=self.university,
            name_en="Business Administration",
            degree="master",
            thesis_type="thesis",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.turkish)
        self.assertEqual(
            program.slug_en,
            "istanbul-atlas-university-business-administration-master-thesis-turkish",
        )

    def test_multilingual_variant_contains_all_structured_languages(self):
        program = Program.objects.create(
            university=self.university,
            name_en="Translation and Interpreting",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.english)
        self._add_language(program, self.turkish, primary=False)
        self.assertEqual(
            program.slug_en,
            "istanbul-atlas-university-translation-and-interpreting-bachelor-english-turkish",
        )

    def test_repeated_save_is_idempotent(self):
        program = Program.objects.create(
            university=self.university,
            name_en="Nursing",
            degree="bachelor",
            created_by=self.actor,
            updated_by=self.actor,
        )
        self._add_language(program, self.turkish)
        expected = "istanbul-atlas-university-nursing-bachelor-turkish"
        program.save()
        program.refresh_from_db()
        self.assertEqual(program.slug_en, expected)
