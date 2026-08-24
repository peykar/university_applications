from django.core.management.base import BaseCommand
from phonenumber_field.phonenumber import PhoneNumber

from apps.core.validators import normalize_phone_number


class Command(BaseCommand):
    help = "Verify TurkDemy phone-number parsing through django-phonenumber-field."

    def handle(self, *args, **options):
        self.stdout.write(
            f"PhoneNumber class: {PhoneNumber.__module__}.{PhoneNumber.__name__}"
        )
        result = normalize_phone_number("+31612345678")
        self.stdout.write(self.style.SUCCESS(f"Parser OK: {result}"))
