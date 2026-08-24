from django.core.management.base import BaseCommand

import phonenumbers
from phonenumbers.phonenumberutil import parse


class Command(BaseCommand):
    help = "Show which phonenumbers package is loaded and verify its parser."

    def handle(self, *args, **options):
        self.stdout.write(f"phonenumbers module: {phonenumbers.__file__}")
        self.stdout.write(
            f"phonenumbers version: {getattr(phonenumbers, '__version__', 'unknown')}"
        )
        result = parse("+31612345678", None)
        self.stdout.write(self.style.SUCCESS(f"Parser OK: {result}"))
