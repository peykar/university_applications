from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse

from apps.core.audit import get_system_user
from apps.geography.models import City, Country, Province
from apps.universities.models import Program, University


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
