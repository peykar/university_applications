from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.core.audit import get_system_user
from apps.universities.models import Program


class Command(BaseCommand):
    help = (
        "Rebuild every Program localized public slug from structured University, "
        "Academic Unit, Department, Program name, degree, thesis type, and "
        "instruction-language data. Canonical collisions receive deterministic "
        "numeric suffixes such as -2 and -3."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show the planned changes without writing them.",
        )

    @staticmethod
    def _resolve_collisions(
        canonical_targets: dict[str, dict[str, list[Program]]],
    ) -> tuple[dict[tuple[str, str], str], list[tuple[str, str, list[Program]]]]:
        """Return per-Program localized targets with deterministic numeric tails."""
        resolved: dict[tuple[str, str], str] = {}
        conflicts: list[tuple[str, str, list[Program]]] = []

        for locale, localized_targets in canonical_targets.items():
            reserved = set(localized_targets)
            assigned: set[str] = set()
            for slug in sorted(localized_targets):
                owners = sorted(localized_targets[slug], key=lambda program: str(program.pk))
                if len(owners) > 1:
                    conflicts.append((locale, slug, owners))

                for index, program in enumerate(owners):
                    candidate = slug
                    if index:
                        suffix = index + 1
                        candidate = f"{slug}-{suffix}"
                        while candidate in reserved or candidate in assigned:
                            suffix += 1
                            candidate = f"{slug}-{suffix}"
                    resolved[(str(program.pk), locale)] = candidate
                    assigned.add(candidate)

        return resolved, conflicts

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
        before_by_program: dict[str, dict[str, str]] = {}
        canonical_targets: dict[str, dict[str, list[Program]]] = {
            locale: {} for locale in ("en", "fa", "tr", "ar")
        }

        for program in programs:
            program_id = str(program.pk)
            before_by_program[program_id] = {
                locale: getattr(program, f"slug_{locale}") for locale in canonical_targets
            }
            program._populate_missing_slugs()
            for locale in canonical_targets:
                slug = getattr(program, f"slug_{locale}")
                if slug:
                    canonical_targets[locale].setdefault(slug, []).append(program)

        resolved_targets, conflicts = self._resolve_collisions(canonical_targets)

        for locale, slug, owners in conflicts:
            resolutions = ", ".join(
                f"{program.pk} -> {resolved_targets[(str(program.pk), locale)]!r}"
                for program in owners
            )
            self.stdout.write(
                self.style.WARNING(
                    f"CONFLICT slug_{locale}={slug!r}; applying numeric tails: {resolutions}."
                )
            )

        planned: list[tuple[Program, dict[str, str]]] = []
        for program in programs:
            program_id = str(program.pk)
            changes: dict[str, str] = {}
            for locale in canonical_targets:
                target = resolved_targets.get((program_id, locale))
                if target is None:
                    continue
                field_name = f"slug_{locale}"
                if before_by_program[program_id][locale] != target:
                    changes[field_name] = target
            if changes:
                planned.append((program, changes))

        for program, changes in planned:
            rendered = ", ".join(f"{key}={value!r}" for key, value in changes.items())
            self.stdout.write(f"{program.pk}: {rendered}")

        if not dry_run and planned:
            # Clear only fields that are about to change so existing unique constraints cannot
            # block deterministic swaps/reassignments during the rebuild transaction.
            for program, changes in planned:
                Program.objects.filter(pk=program.pk).update(
                    **{field_name: "" for field_name in changes}
                )
            updated_at = timezone.now()
            for program, changes in planned:
                Program.objects.filter(pk=program.pk).update(
                    **changes,
                    updated_by=actor,
                    updated_at=updated_at,
                )

        verb = "would update" if dry_run else "updated"
        message = (
            f"Program slug rebuild complete: {verb}={len(planned)}, "
            f"conflicts_resolved={len(conflicts)}."
        )
        self.stdout.write(self.style.SUCCESS(message))
