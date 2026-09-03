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
        cls.province = province
        city = City.objects.create(
            province=province,
            name_en="Istanbul",
            name_fa="استانبول",
            name_tr="İstanbul",
            name_ar="إسطنبول",
            slug_en="istanbul-seo",
            description_en="Study in Istanbul, Türkiye's largest university city.",
            description_fa=("استانبول یکی از مهم‌ترین مقاصد تحصیلی ترکیه است."),
            seo_title_en="Universities in Istanbul, Türkiye",
            seo_description_en=(
                "Compare universities and study programs in Istanbul with TurkDemy."
            ),
            banner="cities/banners/istanbul.jpg",
            banner_alt_en="Istanbul skyline and Bosphorus",
            banner_alt_fa="نمای استانبول و تنگه بسفر",
        )
        cls.city = city
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

    def test_homepage_city_destinations_are_eligible_ranked_and_capped(self):
        for index in range(6):
            city = City.objects.create(
                province=self.province,
                name_en=f"City {index}",
                slug_en=f"city-{index}",
            )
            University.objects.create(
                name_en=f"University {index}",
                slug_en=f"university-{index}",
                city=city,
                university_type="private",
            )

        high_coverage_city = City.objects.create(
            province=self.province,
            name_en="High Coverage City",
            slug_en="high-coverage-city",
        )
        for index in range(2):
            University.objects.create(
                name_en=f"High Coverage University {index}",
                slug_en=f"high-coverage-university-{index}",
                city=high_coverage_city,
                university_type="private",
            )

        City.objects.create(
            province=self.province,
            name_en="Empty City",
            slug_en="empty-city",
        )

        with translation.override("en"):
            response = self.client.get(reverse("home"))
        destinations = list(response.context["study_destinations"])

        self.assertEqual(len(destinations), 5)
        self.assertEqual(destinations[0], high_coverage_city)
        self.assertNotIn("empty-city", {city.slug_en for city in destinations})

    def test_homepage_links_featured_city_destinations_to_canonical_landing_pages(self):
        with translation.override("en"):
            url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Study destinations", html)
        self.assertIn("Where do you want to study?", html)
        self.assertIn(
            'href="/en/universities/cities/istanbul-seo/"',
            html,
        )
        self.assertIn('src="/media/cities/banners/istanbul.jpg"', html)
        self.assertIn('alt="Istanbul skyline and Bosphorus"', html)
        self.assertIn("1 universities", html)
        self.assertIn("1 programs", html)

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

    def test_city_landing_page_has_curated_metadata_schema_and_internal_content(self):
        with translation.override("en"):
            url = reverse("university-city-detail", args=[self.city.slug_en])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("Universities in Istanbul, Türkiye", html)
        self.assertIn(
            "Compare universities and study programs in Istanbul with TurkDemy.",
            html,
        )
        self.assertIn("SEO Test University", html)
        self.assertIn("Computer Engineering", html)
        self.assertIn('name="robots" content="index,follow"', html)
        self.assertIn(
            'src="/media/cities/banners/istanbul.jpg"',
            html,
        )
        self.assertIn('alt="Istanbul skyline and Bosphorus"', html)
        self.assertIn(
            (
                'property="og:image" '
                'content="https://turkdemy.com/media/cities/banners/istanbul.jpg"'
            ),
            html,
        )
        schema = self._schema(response)
        types = {node["@type"] for node in schema["@graph"]}
        self.assertIn("CollectionPage", types)
        self.assertIn("BreadcrumbList", types)
        city_node = next(node for node in schema["@graph"] if node["@type"] == "CollectionPage")
        self.assertEqual(
            city_node["image"],
            "https://turkdemy.com/media/cities/banners/istanbul.jpg",
        )

    def test_city_banner_alt_is_localized(self):
        response = self.client.get("/fa/universities/cities/istanbul-seo/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('alt="نمای استانبول و تنگه بسفر"', html)

    def test_city_without_banner_omits_visible_and_social_image(self):
        self.city.banner = ""
        self.city.save(update_fields=["banner"])
        with translation.override("en"):
            url = reverse("university-city-detail", args=[self.city.slug_en])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertNotIn('class="city-landing-banner"', html)
        self.assertNotIn('property="og:image"', html)
        schema = self._schema(response)
        city_node = next(node for node in schema["@graph"] if node["@type"] == "CollectionPage")
        self.assertNotIn("image", city_node)

    def test_sitemap_contains_city_landing_page(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        xml = response.content.decode()
        self.assertIn(
            "https://turkdemy.com/en/universities/cities/istanbul-seo/",
            xml,
        )
        self.assertIn(
            ('hreflang="fa" href="https://turkdemy.com/fa/universities/cities/istanbul-seo/"'),
            xml,
        )

    def test_city_without_active_university_is_not_public_or_in_sitemap(self):
        empty_city = City.objects.create(
            province=self.city.province,
            name_en="Empty City",
            slug_en="empty-city",
        )
        with translation.override("en"):
            url = reverse("university-city-detail", args=[empty_city.slug_en])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn(
            "https://turkdemy.com/en/universities/cities/empty-city/",
            sitemap,
        )

    def test_city_route_uses_canonical_english_slug_in_persian(self):
        response = self.client.get("/fa/universities/cities/istanbul-seo/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("استانبول", html)
        self.assertIn(
            ('rel="canonical" href="https://turkdemy.com/fa/universities/cities/istanbul-seo/"'),
            html,
        )

    def test_university_detail_links_to_city_landing_page(self):
        with translation.override("en"):
            url = reverse("university-detail", args=[self.university.slug_en])
        response = self.client.get(url)
        self.assertContains(
            response,
            f"/en/universities/cities/{self.city.slug_en}/",
        )

    def test_persian_university_metadata_is_localized(self):
        self.client.cookies["django_language"] = "fa"
        response = self.client.get(f"/fa/universities/{self.university.slug_en}/")
        html = response.content.decode()
        self.assertIn("دانشگاه تست سئو", html)
        self.assertIn("برنامه‌ها و گزینه‌های تحصیلی", html)  # noqa: RUF001
        self.assertIn("استانبول", html)
