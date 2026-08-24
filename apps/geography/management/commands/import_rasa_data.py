
from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import all supported RasaStudy downloaded data into TurkDemy."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            default="data/rasa",
            help="Downloaded RasaStudy data directory.",
        )
        parser.add_argument(
            "--academic-year",
            default="2026-2027",
        )
        parser.add_argument(
            "--semester",
            default="Fall",
        )
        parser.add_argument(
            "--skip-content",
            action="store_true",
        )
        parser.add_argument(
            "--skip-catalogue",
            action="store_true",
        )

    def handle(self, *args, **options):
        source = options["source"]

        if not options["skip_catalogue"]:
            call_command(
                "import_rasa_catalogue",
                source,
                academic_year=options["academic_year"],
                semester=options["semester"],
            )

        if not options["skip_content"]:
            call_command("import_rasa_content", source)

        self.stdout.write(self.style.SUCCESS("All requested RasaStudy imports completed."))
