from django.test import SimpleTestCase
from django.urls import resolve, reverse


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
