from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

import pycountry
from babel import Locale

from university_applications.models import Country


LOCALES = {
    "en": Locale.parse("en"),
    "fa": Locale.parse("fa"),
    "tr": Locale.parse("tr"),
    "ar": Locale.parse("ar"),
}


def localized_name(iso2: str, locale_code: str, fallback: str = "") -> str:
    return LOCALES[locale_code].territories.get(iso2, fallback or "")


def localized_slug(name: str) -> str:
    return slugify(name, allow_unicode=True)


class Command(BaseCommand):
    help = (
        "Populate or update Country records from ISO 3166-1 (pycountry) "
        "and Unicode CLDR translations (Babel)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help=(
                "Mark existing Country rows inactive when their ISO2 code is "
                "not present in the current pycountry dataset."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        seen_iso2: set[str] = set()

        for item in sorted(pycountry.countries, key=lambda c: c.alpha_2):
            iso2 = item.alpha_2
            iso3 = item.alpha_3
            seen_iso2.add(iso2)

            name_en = localized_name(iso2, "en", getattr(item, "name", iso2))
            name_fa = localized_name(iso2, "fa", name_en)
            name_tr = localized_name(iso2, "tr", name_en)
            name_ar = localized_name(iso2, "ar", name_en)

            defaults = {
                "iso3": iso3,
                "name_en": name_en,
                "name_fa": name_fa,
                "name_tr": name_tr,
                "name_ar": name_ar,
                "slug_en": localized_slug(name_en),
                "slug_fa": localized_slug(name_fa),
                "slug_tr": localized_slug(name_tr),
                "slug_ar": localized_slug(name_ar),
                "is_active": True,
            }

            _, created = Country.objects.update_or_create(
                iso2=iso2,
                defaults=defaults,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        deactivated_count = 0
        if options["deactivate_missing"]:
            qs = Country.objects.exclude(iso2__in=seen_iso2).filter(is_active=True)
            deactivated_count = qs.update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                "Countries synchronized successfully. "
                f"Created: {created_count}, "
                f"Updated: {updated_count}, "
                f"Deactivated: {deactivated_count}."
            )
        )
