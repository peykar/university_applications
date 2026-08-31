from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.audit import get_system_user
from apps.universities.models import Program


class Command(BaseCommand):
    help = (
        "Rebuild every Program localized public slug as "
        "<university-slug>-<program-slug>, including thesis type when applicable."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the planned changes without writing them.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = bool(options["dry_run"])
        actor = None if dry_run else get_system_user()
        programs = list(Program.objects.select_related("university").order_by("id"))
        planned: list[tuple[Program, dict[str, str]]] = []
        seen: dict[str, dict[str, str]] = {locale: {} for locale in ("en", "fa", "tr", "ar")}

        for program in programs:
            before = {locale: getattr(program, f"slug_{locale}") for locale in seen}
            program._populate_missing_slugs()
            after = {locale: getattr(program, f"slug_{locale}") for locale in seen}
            for locale, slug in after.items():
                if not slug:
                    continue
                owner = seen[locale].get(slug)
                if owner and owner != str(program.pk):
                    raise CommandError(
                        f"Cannot rebuild: duplicate slug_{locale} {slug!r} would be produced "
                        f"for Program {owner} and {program.pk}."
                    )
                seen[locale][slug] = str(program.pk)
            changes = {
                f"slug_{locale}": after[locale]
                for locale in seen
                if before[locale] != after[locale]
            }
            if changes:
                planned.append((program, changes))

        for program, changes in planned:
            rendered = ", ".join(f"{key}={value!r}" for key, value in changes.items())
            self.stdout.write(f"{program.pk}: {rendered}")
            if not dry_run:
                for key, value in changes.items():
                    setattr(program, key, value)
                program.updated_by = actor
                program.save(update_fields=[*changes.keys(), "updated_by", "updated_at"])

        verb = "would update" if dry_run else "updated"
        message = f"Program slug rebuild complete: {verb}={len(planned)}."
        self.stdout.write(self.style.SUCCESS(message))
