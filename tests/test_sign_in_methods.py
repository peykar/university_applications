from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignInMethodsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="password-123",
        )
        self.client.force_login(self.user)

    def test_default_allauth_connections_url_redirects_to_turkdemy_page(self):
        response = self.client.get("/accounts/3rdparty/")
        self.assertRedirects(
            response,
            reverse("sign-in-methods"),
            fetch_redirect_response=False,
        )

    def test_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("sign-in-methods"))
        self.assertEqual(response.status_code, 302)

    def test_page_uses_provider_icons(self):
        SocialAccount.objects.create(
            user=self.user,
            provider="google",
            uid="google-icon-test",
            extra_data={"email": "customer@example.com"},
        )
        SocialAccount.objects.create(
            user=self.user,
            provider="telegram",
            uid="telegram-icon-test",
            extra_data={"username": "customer"},
        )

        response = self.client.get(reverse("sign-in-methods"))

        self.assertContains(response, "icons/auth/google.svg")
        self.assertContains(response, "icons/auth/telegram.svg")
        self.assertContains(response, "icons/auth/email.svg")

    def test_page_lists_connected_social_accounts(self):
        SocialAccount.objects.create(
            user=self.user,
            provider="google",
            uid="google-123",
            extra_data={"email": "customer@example.com"},
        )

        response = self.client.get(reverse("sign-in-methods"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Google")
        self.assertContains(response, "Connected")

    @patch("allauth.account.models.EmailAddress.send_confirmation")
    def test_add_email_uses_emailaddress_confirmation_api(self, send_confirmation):
        response = self.client.post(
            reverse("add-login-email"),
            {"email": "new@example.com"},
        )

        self.assertEqual(response.status_code, 302)
        address = EmailAddress.objects.get(
            user=self.user,
            email="new@example.com",
        )
        self.assertFalse(address.verified)
        send_confirmation.assert_called_once()
        call = send_confirmation.call_args
        self.assertEqual(call.args, ())
        self.assertIsNotNone(call.kwargs["request"])

    def test_add_email_rejects_email_owned_by_other_user(self):
        other = User.objects.create_user(
            username="other",
            email="other@example.com",
        )
        EmailAddress.objects.create(
            user=other,
            email="other@example.com",
            verified=True,
            primary=True,
        )

        response = self.client.post(
            reverse("add-login-email"),
            {"email": "other@example.com"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "already connected to another TurkDemy account",
            status_code=400,
        )

    def test_cannot_disconnect_last_social_method(self):
        self.user.set_unusable_password()
        self.user.email = None
        self.user.save(update_fields=["password", "email"])

        SocialAccount.objects.create(
            user=self.user,
            provider="telegram",
            uid="telegram-123",
        )

        response = self.client.post(
            reverse(
                "disconnect-social-account",
                kwargs={"provider": "telegram"},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            SocialAccount.objects.filter(
                user=self.user,
                provider="telegram",
            ).exists()
        )

    def test_disconnect_social_account_when_another_method_exists(self):
        EmailAddress.objects.create(
            user=self.user,
            email="customer@example.com",
            verified=True,
            primary=True,
        )
        SocialAccount.objects.create(
            user=self.user,
            provider="telegram",
            uid="telegram-123",
        )

        response = self.client.post(
            reverse(
                "disconnect-social-account",
                kwargs={"provider": "telegram"},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            SocialAccount.objects.filter(
                user=self.user,
                provider="telegram",
            ).exists()
        )
