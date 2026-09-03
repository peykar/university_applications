import json
import re

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from apps.geography.models import City, Country, Province
from apps.universities.models import GeneralField, Program, University


@override_settings(SITE_URL="https://turkdemy.com")
class PublicPageMetadataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        country = Country.objects.create(
            name_en="Türkiye",
            name_fa="ترکیه",
            name_tr="Türkiye",
            name_ar="تركيا",
            slug_en="turkiye-seo",
            iso2="TR",
            iso3="TUR",
        )
        province = Province.objects.create(
            country=country,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            slug_en="istanbul-seo",
        )
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            slug_en="istanbul-seo",
        )
        cls.university = University.objects.create(
            name_en="SEO Test University",
            name_fa="دانشگاه تست سئو",
            name_tr="SEO Test Üniversitesi",
            name_ar="جامعة اختبار سيو",
            slug_en="seo-test-university",
            city=city,
            university_type="private",
            website="https://example.edu",
        )
        cls.program = Program.objects.create(
            university=cls.university,
            name_en="Computer Engineering",
            name_fa="مهندسی کامپیوتر",
            name_tr="Bilgisayar Mühendisliği",
            name_ar="هندسة الحاسوب",
            slug_en="seo-test-university-computer-engineering",
            degree="bachelor",
        )
        cls.general_field = GeneralField.objects.create(
            name_en="Engineering",
            name_fa="مهندسی",
            name_tr="Mühendislik",
            name_ar="الهندسة",
            slug_en="engineering",
            slug_fa="mohandesi",
            slug_tr="muhendislik",
            slug_ar="engineering-ar",
            description_en="Explore engineering degrees in Türkiye.",
            description_fa="برنامه‌های مهندسی در ترکیه را بررسی کنید.",
            seo_title_en="Engineering Programs in Türkiye",
            seo_description_en=("Compare engineering programs and universities in Türkiye."),
        )
        cls.program.general_fields.add(cls.general_field)

    def _schema(self, response):
        html = response.content.decode()
        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        return json.loads(match.group(1))

    def test_static_public_pages_have_specific_metadata_and_schema(self):
        cases = [
            ("home", "Study in Türkiye", "WebSite"),
            ("university-list", "Universities in Türkiye", "CollectionPage"),
            ("program-list", "University Programs in Türkiye", "CollectionPage"),
            ("faq", "Study in Türkiye FAQ", "FAQPage"),
            ("about", "About TurkDemy", "AboutPage"),
            ("contact", "Contact TurkDemy", "ContactPage"),
        ]
        for viewname, title_text, schema_type in cases:
            with self.subTest(viewname=viewname):
                with translation.override("en"):
                    url = reverse(viewname)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertIn(title_text, html)
                self.assertNotIn(
                    'name="description" content="Study in Türkiye with TurkDemy."',
                    html,
                )
                schema = self._schema(response)
                schema_types = {node.get("@type") for node in schema.get("@graph", [schema])}
                self.assertIn(schema_type, schema_types)

    def test_university_detail_has_entity_metadata_and_schema(self):
        with translation.override("en"):
            url = reverse("university-detail", args=[self.university.slug_en])
        response = self.client.get(url)
        html = response.content.decode()
        self.assertIn("SEO Test University Programs & Study Options", html)
        self.assertIn('property="og:title"', html)
        schema = self._schema(response)
        university_node = next(
            node for node in schema["@graph"] if node["@type"] == "CollegeOrUniversity"
        )
        self.assertEqual(university_node["name"], "SEO Test University")
        self.assertEqual(university_node["sameAs"], "https://example.edu")

    def test_program_detail_has_program_and_breadcrumb_schema(self):
        with translation.override("en"):
            url = reverse("program-detail", args=[self.program.slug_en])
        response = self.client.get(url)
        html = response.content.decode()
        self.assertIn("Computer Engineering", html)
        self.assertIn("tuition, intakes and study details", html)
        schema = self._schema(response)
        types = {node["@type"] for node in schema["@graph"]}
        self.assertIn("EducationalOccupationalProgram", types)
        self.assertIn("BreadcrumbList", types)

    def test_general_field_landing_page_has_curated_metadata_and_schema(self):
        with translation.override("en"):
            url = reverse("program-field-detail", args=[self.general_field.slug_en])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Engineering Programs in Türkiye", html)
        self.assertIn("Compare engineering programs and universities in Türkiye.", html)
        self.assertIn("Computer Engineering", html)
        self.assertIn('name="robots" content="index,follow"', html)
        schema = self._schema(response)
        types = {node["@type"] for node in schema["@graph"]}
        self.assertIn("CollectionPage", types)
        self.assertIn("BreadcrumbList", types)

    def test_sitemap_contains_general_field_landing_page(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        xml = response.content.decode()
        self.assertIn(
            "https://turkdemy.com/en/programs/fields/engineering/",
            xml,
        )
        self.assertIn(
            'hreflang="fa" href="https://turkdemy.com/fa/programs/fields/engineering/"',
            xml,
        )

    def test_general_field_route_uses_canonical_english_slug_in_persian(self):
        response = self.client.get("/fa/programs/fields/engineering/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("مهندسی", html)
        self.assertIn(
            ('rel="canonical" href="https://turkdemy.com/fa/programs/fields/engineering/"'),
            html,
        )

    def test_persian_university_metadata_is_localized(self):
        self.client.cookies["django_language"] = "fa"
        response = self.client.get(f"/fa/universities/{self.university.slug_en}/")
        html = response.content.decode()
        self.assertIn("دانشگاه تست سئو", html)
        self.assertIn("برنامه‌ها و گزینه‌های تحصیلی", html)  # noqa: RUF001
        self.assertIn("استانبول", html)
