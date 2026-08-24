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

    def test_social_login_is_post_only(self):
        self.assertFalse(settings.SOCIALACCOUNT_LOGIN_ON_GET)
