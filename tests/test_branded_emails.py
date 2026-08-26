from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.services.email_branding import render_branded_email_html


class BrandedEmailTests(SimpleTestCase):
    def test_login_and_verification_codes_are_five_digit_numeric(self):
        expected = {"numeric": True, "dashed": False, "length": 5}
        self.assertEqual(settings.ACCOUNT_LOGIN_BY_CODE_FORMAT, expected)
        self.assertEqual(
            settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_FORMAT,
            expected,
        )

    def test_allauth_uses_turkdemy_account_adapter(self):
        self.assertEqual(
            settings.ACCOUNT_ADAPTER,
            "apps.accounts.adapters.TurkDemyAccountAdapter",
        )

    def test_shared_branded_email_template_renders(self):
        html = render_branded_email_html(
            subject="Test email",
            text_body="Hello from TurkDemy.",
        )
        self.assertIn("TurkDemy", html)
        self.assertIn("Test email", html)
        self.assertIn("Hello from TurkDemy.", html)

    def test_login_code_has_dedicated_html_email(self):
        path = (
            Path(settings.BASE_DIR) / "templates" / "account" / "email" / "login_code_message.html"
        )
        source = path.read_text(encoding="utf-8")
        self.assertIn('{% extends "emails/base.html" %}', source)
        self.assertIn("{{ code }}", source)
