from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

import pycountry
from babel import Locale

from apps.core.audit import audited_update_or_create, get_system_user
from apps.geography.models import Country


LOCALES = {code: Locale.parse(code) for code in ("en", "fa", "tr", "ar")}


class Command(BaseCommand):
    help = "Populate or update countries from pycountry and Babel/CLDR."

    @transaction.atomic
    def handle(self, *args, **options):
        created = updated = 0
        system_user = get_system_user()
        for item in pycountry.countries:
            iso2 = item.alpha_2
            names = {
                code: LOCALES[code].territories.get(iso2, item.name)
                for code in LOCALES
            }
            _, was_created = audited_update_or_create(
                Country.objects,
                lookup={"iso2": iso2},
                defaults={
                    "iso3": item.alpha_3,
                    "name_en": names["en"],
                    "name_fa": names["fa"],
                    "name_tr": names["tr"],
                    "name_ar": names["ar"],
                    "slug_en": slugify(names["en"], allow_unicode=True),
                    "slug_fa": slugify(names["fa"], allow_unicode=True),
                    "slug_tr": slugify(names["tr"], allow_unicode=True),
                    "slug_ar": slugify(names["ar"], allow_unicode=True),
                    "is_active": True,
                },
                actor=system_user,
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(self.style.SUCCESS(f"Created: {created}, Updated: {updated}"))
