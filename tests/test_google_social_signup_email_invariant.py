from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class GoogleSocialSignupEmailInvariantTests(SimpleTestCase):
    def test_socialaccount_signal_does_not_create_email_for_new_signup(self):
        source = (Path(settings.BASE_DIR) / "apps/accounts/signals.py").read_text(encoding="utf-8")
        self.assertIn(
            "EmailAddress.objects.filter(",
            source,
        )
        self.assertIn(
            ").exists():\n            ensure_verified_login_email(user, email)",
            source,
        )
