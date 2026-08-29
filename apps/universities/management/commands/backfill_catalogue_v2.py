from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.universities.models import Program, ProgramInstructionLanguage


class Command(BaseCommand):
    help = (
        "Backfill Catalogue v2 canonical duration and instruction-language data "
        "from legacy Program fields. Safe to run repeatedly."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        durations = 0
        languages = 0

        for program in Program.objects.select_related("program_language").iterator():
            update_fields: list[str] = []
            if program.duration_months is None and program.duration is not None:
                program.duration_months = program.duration * 12
                update_fields.append("duration_months")
            if update_fields:
                program.save(update_fields=[*update_fields, "updated_at"])
                durations += 1

            if program.program_language_id:
                _, created = ProgramInstructionLanguage.objects.get_or_create(
                    program=program,
                    language_id=program.program_language_id,
                    defaults={"is_primary": True},
                )
                languages += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalogue v2 backfill complete: durations={durations}, "
                f"language associations={languages}."
            )
        )
