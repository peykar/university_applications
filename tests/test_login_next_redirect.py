from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class LoginNextRedirectTests(SimpleTestCase):
    def _template(self, name: str) -> str:
        return (Path(settings.BASE_DIR) / "templates" / "account" / name).read_text(
            encoding="utf-8"
        )

    def test_email_code_link_preserves_next_destination(self):
        source = self._template("login.html")
        self.assertIn("request.GET.next|urlencode", source)
        self.assertIn("account_request_login_code", source)

    def test_social_login_providers_receive_next_destination(self):
        source = self._template("login.html")
        self.assertIn(
            "provider_login_url 'google' process='login' next=request.GET.next",
            source,
        )
        self.assertIn(
            "provider_login_url 'telegram' process='login' next=request.GET.next",
            source,
        )

    def test_request_code_page_preserves_next_when_switching_methods(self):
        source = self._template("request_login_code.html")
        self.assertIn("request.GET.next|urlencode", source)
        self.assertIn("account_login", source)
