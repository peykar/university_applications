from allauth.socialaccount.models import SocialAccount
from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.accounts.social_email import (
    ensure_verified_login_email,
    google_verified_email,
)


class Command(BaseCommand):
    help = "Synchronize verified emails from connected social accounts."

    def handle(self, *args, **options) -> None:
        synchronized = 0
        skipped = 0

        accounts = SocialAccount.objects.filter(provider="google").select_related("user")
        for account in accounts:
            user = account.user
            email = google_verified_email(account.extra_data)
            if not isinstance(user, User) or not email:
                skipped += 1
                continue

            address = ensure_verified_login_email(user, email)
            if address.user_id == user.pk and address.verified:
                synchronized += 1
                self.stdout.write(self.style.SUCCESS(f"Verified {email} for user {user.pk}"))
            else:
                skipped += 1
                self.stderr.write(
                    self.style.WARNING(f"Skipped {email}: it belongs to another account")
                )

        self.stdout.write(f"Done. synchronized={synchronized}, skipped={skipped}")
