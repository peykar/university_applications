from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase
from django.utils import timezone
from django.utils.translation import override

from apps.core.localization import (
    localized_date,
    localized_datetime,
    localized_time,
)


class LocaleDateTimePresentationTests(SimpleTestCase):
    def test_persian_date_uses_solar_hijri_month_and_digits(self):
        with override("fa"):
            rendered = localized_date(date(2026, 9, 3))

        self.assertEqual(rendered, "\u06f1\u06f2 شهریور \u06f1\u06f4\u06f0\u06f5")

    def test_persian_historical_date_is_converted_without_mutation(self):
        value = date(2025, 11, 21)

        with override("fa"):
            rendered = localized_date(value)

        self.assertEqual(rendered, "\u06f3\u06f0 آبان \u06f1\u06f4\u06f0\u06f4")
        self.assertEqual(value, date(2025, 11, 21))

    def test_persian_datetime_uses_solar_hijri_and_persian_digits(self):
        value = datetime(2026, 9, 3, 1, 37)

        with override("fa"):
            rendered = localized_datetime(value)

        self.assertEqual(
            rendered,
            "\u06f1\u06f2 شهریور \u06f1\u06f4\u06f0\u06f5، \u06f0\u06f1:\u06f3\u06f7",
        )

    def test_persian_short_datetime_omits_year_but_keeps_jalali_month(self):
        value = datetime(2026, 9, 3, 1, 37)

        with override("fa"):
            rendered = localized_datetime(value, style="short")

        self.assertEqual(rendered, "\u06f1\u06f2 شهریور، \u06f0\u06f1:\u06f3\u06f7")

    def test_timezone_conversion_precedes_persian_calendar_conversion(self):
        value = datetime(2026, 3, 20, 23, 30, tzinfo=UTC)

        with timezone.override(ZoneInfo("Europe/Amsterdam")), override("fa"):
            rendered = localized_datetime(value)

        self.assertEqual(
            rendered,
            "\u06f1 فروردین \u06f1\u06f4\u06f0\u06f5، \u06f0\u06f0:\u06f3\u06f0",
        )

    def test_english_remains_gregorian(self):
        with override("en"):
            rendered = localized_datetime(datetime(2026, 9, 3, 1, 37))

        self.assertEqual(rendered, "Sep 3, 2026, 01:37")

    def test_turkish_remains_gregorian_with_localized_month(self):
        with override("tr"):
            rendered = localized_date(date(2026, 9, 3))

        self.assertEqual(rendered, "3 Eyl 2026")

    def test_arabic_remains_gregorian_with_arabic_indic_digits(self):
        with override("ar"):
            rendered = localized_date(date(2026, 9, 3))

        self.assertIn("\u0662\u0660\u0662\u0666", rendered)
        self.assertIn("\u0663", rendered)
        self.assertNotIn("1405", rendered)
        self.assertNotIn("\u06f1\u06f4\u06f0\u06f5", rendered)

    def test_localized_time_uses_active_locale_numerals(self):
        value = datetime(2026, 9, 3, 1, 7)

        with override("fa"):
            self.assertEqual(localized_time(value), "\u06f0\u06f1:\u06f0\u06f7")
        with override("ar"):
            self.assertEqual(localized_time(value), "\u0660\u0661:\u0660\u0667")
        with override("en"):
            self.assertEqual(localized_time(value), "01:07")

    def test_none_values_render_empty(self):
        self.assertEqual(localized_date(None), "")
        self.assertEqual(localized_datetime(None), "")
        self.assertEqual(localized_time(None), "")

    def test_translation_enabled_templates_use_canonical_display_filters(self):
        allowed_machine_filters = {
            (
                Path("templates/leads/lead_section.html"),
                "message.created_at|date:'c'",
            ),
            (
                Path("templates/agents/includes/communication_workspace.html"),
                "communication.occurred_at|date:'Y-m-d\\\\TH:i'",
            ),
        }
        found_machine_filters = set()
        raw_human_filters = []

        for template_path in Path("templates").rglob("*.html"):
            source = template_path.read_text()
            for line in source.splitlines():
                if "|date:" not in line and "|time:" not in line:
                    continue
                matched_allowed = False
                for allowed_path, marker in allowed_machine_filters:
                    if template_path == allowed_path and marker in line:
                        found_machine_filters.add((allowed_path, marker))
                        matched_allowed = True
                if not matched_allowed:
                    raw_human_filters.append((template_path, line.strip()))

        self.assertEqual(raw_human_filters, [])
        self.assertEqual(found_machine_filters, allowed_machine_filters)

    def test_known_date_only_surfaces_use_localized_date(self):
        checks = {
            "templates/public/program_detail.html": "offering.deadline|localized_date",
            "templates/leads/lead_section.html": "lead.birthdate|localized_date",
            "templates/agents/applicant_section.html": "lead.birthdate|localized_date",
            "templates/agents/application_list.html": "application.updated_at|localized_date",
            "templates/agents/workspace_dashboard.html": "todo.due_date|localized_date",
            "templates/agents/includes/todo_workspace.html": "todo.due_date|localized_date",
        }

        for filename, marker in checks.items():
            with self.subTest(filename=filename):
                self.assertIn(marker, Path(filename).read_text())
