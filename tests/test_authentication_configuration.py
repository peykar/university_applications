from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


class AuthenticationConfigurationTests(SimpleTestCase):
    def test_allauth_is_configured(self):
        self.assertIn("allauth.account", settings.INSTALLED_APPS)
        self.assertIn("allauth.socialaccount", settings.INSTALLED_APPS)
        self.assertTrue(settings.ACCOUNT_LOGIN_BY_CODE_ENABLED)
        self.assertTrue(settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED)
        self.assertEqual(settings.ACCOUNT_LOGIN_METHODS, {"email"})

    def test_authentication_urls_are_stable(self):
        self.assertEqual(reverse("account_login"), "/accounts/login/")
        self.assertEqual(reverse("account_signup"), "/accounts/signup/")

    def test_social_login_does_not_require_second_email_verification(self):
        self.assertEqual(settings.ACCOUNT_EMAIL_VERIFICATION, "mandatory")
        self.assertEqual(settings.SOCIALACCOUNT_EMAIL_VERIFICATION, "none")

    def test_login_template_uses_provider_icons(self):
        from pathlib import Path

        from django.conf import settings

        template = Path(settings.BASE_DIR) / "templates" / "account" / "login.html"
        source = template.read_text(encoding="utf-8")
        self.assertIn("icons/auth/google.svg", source)
        self.assertIn("icons/auth/telegram.svg", source)

    def test_social_login_is_post_only(self):
        self.assertFalse(settings.SOCIALACCOUNT_LOGIN_ON_GET)
