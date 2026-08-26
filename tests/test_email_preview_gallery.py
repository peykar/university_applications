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

    def test_superuser_can_preview_login_code_in_every_language(self):
        self.client.force_login(self.superuser)
        for language in ("en", "fa", "tr", "ar"):
            response = self.client.get(
                reverse(
                    "email-preview-detail",
                    args=["login_code", language],
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "48317")

    def test_registry_covers_all_allauth_account_email_templates(self):
        errors = [error for error in checks.run_checks() if error.id == "turkdemy.E001"]
        self.assertEqual(errors, [])

    def test_registry_has_unique_template_prefixes(self):
        prefixes = [spec.template_prefix for spec in EMAIL_PREVIEW_REGISTRY.values()]
        self.assertEqual(len(prefixes), len(set(prefixes)))
