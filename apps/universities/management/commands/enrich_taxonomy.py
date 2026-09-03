from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.audit import get_system_user
from apps.geography.models import City
from apps.universities.models import GeneralField, Program

_DATA_DIR = Path(__file__).with_name("data")


def _load_data(filename: str) -> Any:
    with (_DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


GENERAL_FIELDS = _load_data("general_fields.json")

CITY_ENRICHMENT = _load_data("city_enrichment.json")

PROGRAM_FIELD_MAP = _load_data("program_field_map.json")

SKIPPED_PROGRAMS = {
    "b16d8718-7e8a-46d8-bb68-50913baad85e": (
        "Malformed catalogue record whose English name is only 'biruni'; manual review required."
    ),
}


class Command(BaseCommand):
    help = (
        "One-time curated TurkDemy taxonomy enrichment: update City SEO content, "
        "create/update GeneralFields, and add verified Program-GeneralField mappings."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apply all work in a transaction and roll it back after reporting.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        actor = get_system_user()
        created_fields = 0
        updated_fields = 0

        field_by_slug = {}
        for data in GENERAL_FIELDS:
            slug = data["slug_en"]
            defaults = dict(data)
            defaults.pop("slug_en")
            defaults["updated_by"] = actor
            field, created = GeneralField.objects.update_or_create(
                slug_en=slug,
                defaults=defaults,
                create_defaults={**defaults, "created_by": actor},
            )
            field_by_slug[slug] = field
            if created:
                created_fields += 1
            else:
                updated_fields += 1

        city_slug = CITY_ENRICHMENT["slug_en"]
        try:
            city = City.objects.get(slug_en=city_slug)
        except City.DoesNotExist as exc:
            raise CommandError(
                f"Expected existing City slug_en={city_slug!r}; "
                "refusing to create a duplicate city."
            ) from exc

        city_fields = {
            key: value
            for key, value in CITY_ENRICHMENT.items()
            if key.startswith("description_")
            or key.startswith("seo_title_")
            or key.startswith("seo_description_")
        }
        for key, value in city_fields.items():
            setattr(city, key, value)
        city.updated_by = actor
        city.save(update_fields=[*city_fields, "updated_by", "updated_at"])

        mapped_programs = 0
        added_links = 0
        missing_programs = []
        for raw_id, slugs in PROGRAM_FIELD_MAP.items():
            try:
                program = Program.objects.get(pk=UUID(raw_id), is_active=True)
            except Program.DoesNotExist:
                missing_programs.append(raw_id)
                continue

            fields = [field_by_slug[slug] for slug in slugs]
            before = set(program.general_fields.values_list("pk", flat=True))
            program.general_fields.add(*fields)
            after = set(program.general_fields.values_list("pk", flat=True))
            added_links += len(after - before)
            mapped_programs += 1

        if options["dry_run"]:
            transaction.set_rollback(True)
            mode = "Dry run complete; all database changes were rolled back."
        else:
            mode = "Taxonomy enrichment complete."

        self.stdout.write(self.style.SUCCESS(mode))
        self.stdout.write(
            f"GeneralFields: created={created_fields}, updated={updated_fields}; "
            f"city={city.name_en}; programs_mapped={mapped_programs}; links_added={added_links}."
        )
        if missing_programs:
            self.stdout.write(
                self.style.WARNING(
                    f"{len(missing_programs)} mapped program UUID(s) were not "
                    "present/active in this database and were skipped."
                )
            )
        for program_id, reason in SKIPPED_PROGRAMS.items():
            self.stdout.write(self.style.WARNING(f"Manual review: {program_id}: {reason}"))
