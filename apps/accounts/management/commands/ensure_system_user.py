from django.core.management.base import BaseCommand

from apps.core.audit import get_system_user


class Command(BaseCommand):
    help = "Create/update the configured non-human system audit user."

    def handle(self, *args, **options):
        user = get_system_user()
        self.stdout.write(
            self.style.SUCCESS(
                f"System user ready: username={user.username!r}, email={user.email!r}, "
                f"active={user.is_active}, staff={user.is_staff}, superuser={user.is_superuser}."
            )
        )
