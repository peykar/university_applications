from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.social_email import (
    ensure_verified_login_email,
    google_verified_email,
)

User = get_user_model()


class SocialEmailSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="google-user",
            email="person@example.com",
            password="existing-password",
        )

    def test_google_verified_email_payload(self):
        self.assertEqual(
            google_verified_email({"email": "Person@Example.com", "email_verified": True}),
            "person@example.com",
        )
        self.assertIsNone(
            google_verified_email({"email": "person@example.com", "email_verified": False})
        )

    def test_google_socialaccount_save_marks_matching_email_verified(self):
        address = EmailAddress.objects.create(
            user=self.user,
            email="person@example.com",
            verified=False,
            primary=False,
        )

        SocialAccount.objects.create(
            user=self.user,
            provider="google",
            uid="google-1",
            extra_data={
                "email": "person@example.com",
                "email_verified": True,
            },
        )

        address.refresh_from_db()
        self.assertTrue(address.verified)
        self.assertTrue(address.primary)

        self.user.refresh_from_db()
        self.assertTrue(self.user.has_usable_password())
        self.assertTrue(self.user.check_password("existing-password"))

    def test_sync_does_not_steal_email_from_another_user(self):
        other = User.objects.create_user(
            username="other",
            email="other@example.com",
        )
        foreign = EmailAddress.objects.create(
            user=other,
            email="shared@example.com",
            verified=True,
            primary=True,
        )

        result = ensure_verified_login_email(self.user, "shared@example.com")

        self.assertEqual(result.pk, foreign.pk)
        self.assertFalse(
            EmailAddress.objects.filter(
                user=self.user,
                email="shared@example.com",
            ).exists()
        )
