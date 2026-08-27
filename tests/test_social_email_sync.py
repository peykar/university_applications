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

    def test_new_google_socialaccount_does_not_precreate_emailaddress(self):
        new_user = User.objects.create_user(
            username="new-google-user",
            email="new-google@example.com",
        )
        self.assertFalse(EmailAddress.objects.filter(user=new_user).exists())

        SocialAccount.objects.create(
            user=new_user,
            provider="google",
            uid="google-new-user",
            extra_data={
                "email": "new-google@example.com",
                "email_verified": True,
            },
        )

        # allauth itself must create the EmailAddress later in
        # SocialLogin.save() -> setup_user_email(). The post_save signal must
        # not create it first.
        self.assertFalse(EmailAddress.objects.filter(user=new_user).exists())
