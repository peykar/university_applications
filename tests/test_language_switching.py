from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    LANGUAGES=(("en", "English"), ("fa", "Persian"), ("tr", "Turkish"), ("ar", "Arabic")),
)
class LanguageSwitchingTests(TestCase):
    def test_switches_locale_prefixed_path_and_preserves_query_string(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "fa", "next": "/en/programs/?field=engineering&page=2"},
        )

        self.assertRedirects(
            response,
            "/fa/programs/?field=engineering&page=2",
            fetch_redirect_response=False,
        )
        self.assertEqual(response.cookies["django_language"].value, "fa")

    def test_falls_back_to_prefix_replacement_when_url_translation_cannot_resolve(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "tr", "next": "/fa/not-a-resolvable-product-route/?page=3"},
        )

        self.assertRedirects(
            response,
            "/tr/not-a-resolvable-product-route/?page=3",
            fetch_redirect_response=False,
        )

    def test_non_prefixed_safe_path_uses_cookie_for_locale_selection(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "ar", "next": "/accounts/login/?next=/en/"},
        )

        self.assertRedirects(
            response,
            "/accounts/login/?next=/en/",
            fetch_redirect_response=False,
        )
        self.assertEqual(response.cookies["django_language"].value, "ar")

    def test_rejects_external_next_url(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "fa", "next": "https://example.org/en/programs/"},
        )

        self.assertRedirects(response, "/", fetch_redirect_response=False)
