from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


class EmailCodeLoginRoutingTests(SimpleTestCase):
    def test_allauth_login_code_urls_are_distinct_from_signup(self):
        self.assertEqual(
            reverse("account_request_login_code"),
            "/accounts/login/code/",
        )
        self.assertEqual(
            reverse("account_confirm_login_code"),
            "/accounts/login/code/confirm/",
        )
        self.assertEqual(reverse("account_signup"), "/accounts/signup/")

    def test_login_template_links_directly_to_login_code_endpoint(self):
        source = (Path(settings.BASE_DIR) / "templates" / "account" / "login.html").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "href=\"{% url 'account_request_login_code' %}\"",
            source,
        )
        self.assertNotIn(
            'href="{{ request_login_code_url }}"',
            source,
        )

    def test_request_code_form_posts_to_login_code_endpoint(self):
        source = (
            Path(settings.BASE_DIR) / "templates" / "account" / "request_login_code.html"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "action=\"{% url 'account_request_login_code' %}\"",
            source,
        )

    def test_confirm_code_form_posts_to_confirm_login_endpoint(self):
        source = (
            Path(settings.BASE_DIR) / "templates" / "account" / "confirm_login_code.html"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "action=\"{% url 'account_confirm_login_code' %}\"",
            source,
        )
