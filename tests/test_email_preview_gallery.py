from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import checks
from django.test import TestCase
from django.urls import reverse

from apps.core.email_previews import EMAIL_PREVIEW_REGISTRY


class EmailPreviewGalleryTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username="email-preview-admin",
            email="admin@example.com",
            password="test-password",
        )
        self.normal_user = user_model.objects.create_user(
            username="email-preview-user",
            email="user@example.com",
            password="test-password",
        )

    def test_gallery_is_superuser_only(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("email-preview-gallery"))
        self.assertEqual(response.status_code, 404)

    def test_superuser_can_open_gallery(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("email-preview-gallery"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email Preview Gallery")
        self.assertContains(response, "Sign-in code")

    def test_every_registered_email_renders_every_supported_language(self):
        self.client.force_login(self.superuser)

        for email_type in EMAIL_PREVIEW_REGISTRY:
            for language, _name in settings.LANGUAGES:
                response = self.client.get(
                    reverse(
                        "email-preview-html",
                        args=[email_type, language],
                    )
                )
                self.assertEqual(
                    response.status_code,
                    200,
                    msg=f"{email_type}/{language} failed to render",
                )
                self.assertIn("text/html", response["Content-Type"])
                self.assertGreater(
                    len(response.content),
                    100,
                    msg=f"{email_type}/{language} rendered an empty HTML body",
                )

    def test_superuser_can_preview_login_code_in_every_language(self):
        self.client.force_login(self.superuser)

        for language, _name in settings.LANGUAGES:
            html_url = reverse(
                "email-preview-html",
                args=["login_code", language],
            )
            response = self.client.get(
                reverse(
                    "email-preview-detail",
                    args=["login_code", language],
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f'src="{html_url}"')

    def test_raw_html_preview_is_superuser_only_and_has_body(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse(
                "email-preview-html",
                args=["password_reset_key", "fa"],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])
        self.assertGreater(len(response.content), 100)
        self.assertIn("ترک‌دمی", response.content.decode())
        self.assertNotIn("TurkDemy", response.content.decode())

        self.client.force_login(self.normal_user)
        response = self.client.get(
            reverse(
                "email-preview-html",
                args=["password_reset_key", "fa"],
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_registry_covers_all_allauth_account_email_templates(self):
        errors = [error for error in checks.run_checks() if error.id == "turkdemy.E001"]
        self.assertEqual(errors, [])

    def test_registry_has_unique_template_prefixes(self):
        prefixes = [spec.template_prefix for spec in EMAIL_PREVIEW_REGISTRY.values()]
        self.assertEqual(len(prefixes), len(set(prefixes)))

    def test_persian_and_arabic_previews_localize_brand_name(self):
        self.client.force_login(self.superuser)

        for language in ("fa", "ar"):
            response = self.client.get(
                reverse(
                    "email-preview-html",
                    args=["password_reset_key", language],
                )
            )
            self.assertEqual(response.status_code, 200)
            html = response.content.decode()
            if language == "fa":
                self.assertIn("ترک‌دمی", html)
            else:
                self.assertIn("ترك ديمي", html)
