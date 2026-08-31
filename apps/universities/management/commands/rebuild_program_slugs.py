from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.audit import get_system_user
from apps.universities.models import Program


class Command(BaseCommand):
    help = (
        "Rebuild every Program localized public slug from structured University, "
        "Academic Unit, Department, Program name, degree, thesis type, and "
        "instruction-language data."
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
        programs = list(
            Program.objects.select_related(
                "university",
                "academic_unit",
                "department",
            ).order_by("id")
        )
        candidates: list[tuple[Program, dict[str, str]]] = []
        targets: dict[str, dict[str, list[Program]]] = {
            locale: {} for locale in ("en", "fa", "tr", "ar")
        }

        for program in programs:
            before = {locale: getattr(program, f"slug_{locale}") for locale in targets}
            program._populate_missing_slugs()
            after = {locale: getattr(program, f"slug_{locale}") for locale in targets}
            for locale, slug in after.items():
                if slug:
                    targets[locale].setdefault(slug, []).append(program)
            changes = {
                f"slug_{locale}": after[locale]
                for locale in targets
                if before[locale] != after[locale]
            }
            if changes:
                candidates.append((program, changes))

        conflicts: list[tuple[str, str, list[Program]]] = []
        conflicting_program_ids: set[str] = set()
        for locale, localized_targets in targets.items():
            for slug, owners in localized_targets.items():
                if len(owners) < 2:
                    continue
                conflicts.append((locale, slug, owners))
                conflicting_program_ids.update(str(program.pk) for program in owners)

        for locale, slug, owners in conflicts:
            owner_ids = ", ".join(str(program.pk) for program in owners)
            self.stdout.write(
                self.style.WARNING(
                    f"CONFLICT slug_{locale}={slug!r}; skipping Programs: {owner_ids}."
                )
            )

        planned = [
            (program, changes)
            for program, changes in candidates
            if str(program.pk) not in conflicting_program_ids
        ]

        for program, changes in planned:
            rendered = ", ".join(f"{key}={value!r}" for key, value in changes.items())
            self.stdout.write(f"{program.pk}: {rendered}")
            if not dry_run:
                for key, value in changes.items():
                    setattr(program, key, value)
                program.updated_by = actor
                program.save(update_fields=[*changes.keys(), "updated_by", "updated_at"])

        verb = "would update" if dry_run else "updated"
        message = (
            f"Program slug rebuild complete: {verb}={len(planned)}, "
            f"conflicts={len(conflicts)}, skipped_programs={len(conflicting_program_ids)}."
        )
        self.stdout.write(self.style.SUCCESS(message))
