from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.adapters import TurkDemySocialAccountAdapter

User = get_user_model()


class SocialAccountPasswordPreservationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="legacy-admin",
            email="legacy@example.com",
            password="existing-password-123",
            is_staff=True,
            is_superuser=True,
        )

    def test_verified_google_email_is_recorded_before_email_authentication(self):
        adapter = TurkDemySocialAccountAdapter()

        sociallogin = SocialLogin(
            user=User(email="legacy@example.com"),
            account=SocialAccount(
                provider="google",
                uid="google-user-1",
            ),
            email_addresses=[
                EmailAddress(
                    email="legacy@example.com",
                    verified=True,
                    primary=True,
                )
            ],
        )

        adapter.can_authenticate_by_email = lambda login, email: True  # type: ignore[method-assign]

        result = adapter.authenticate_by_email(sociallogin)

        self.assertIsNotNone(result)
        assert result is not None
        matched_user, matched_email = result

        self.assertEqual(matched_user.pk, self.user.pk)
        self.assertEqual(matched_email, "legacy@example.com")

        address = EmailAddress.objects.get(
            user=self.user,
            email="legacy@example.com",
        )
        self.assertTrue(address.verified)
        self.assertTrue(address.primary)

        self.user.refresh_from_db()
        self.assertTrue(self.user.has_usable_password())
        self.assertTrue(self.user.check_password("existing-password-123"))
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)
