from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.universities.models import University

EXPORT_SCHEMA_VERSION = 1
LOCALIZED_LANGUAGES = ("en", "fa", "tr", "ar")


class Command(BaseCommand):
    help = (
        "Dump catalogue data for one University to a UTF-8 JSON file. "
        "The export contains catalogue/geography content only and excludes applicant, "
        "student, application, messaging, and other customer operational data."
    )

    def add_arguments(self, parser):
        parser.add_argument("university_id", help="UUID of the University to export")
        parser.add_argument(
            "--output",
            help=(
                "Destination JSON file. Defaults to "
                "university_<university-id>_catalogue.json in the current directory."
            ),
        )

    def handle(self, *args, **options):
        university = self._get_university(options["university_id"])
        output = Path(options["output"] or f"university_{university.pk}_catalogue.json")
        output.parent.mkdir(parents=True, exist_ok=True)

        payload = self._serialize_university(university)
        output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(
                "University catalogue dump complete. "
                f"University={university.name_en!r}; "
                f"Academic units={len(payload['academic_units'])}; "
                f"Departments={len(payload['departments'])}; "
                f"Programs={len(payload['programs'])}; "
                f"Offerings={sum(len(program['offerings']) for program in payload['programs'])}; "
                f"Catalogue sources={len(payload['catalogue_sources'])}; "
                f"Media={len(payload['media'])}; "
                f"Output={output}."
            )
        )

    def _get_university(self, university_id: str) -> University:
        try:
            return (
                University.objects.select_related(
                    "city__province__country",
                )
                .prefetch_related(
                    "media",
                    "academic_units",
                    "departments",
                    "catalogue_sources__academic_year",
                    "programs__academic_unit",
                    "programs__department",
                    "programs__program_language",
                    "programs__instruction_language_rows__language",
                    "programs__offerings__academic_year",
                    "programs__offerings__semester",
                    "programs__offerings__source",
                )
                .get(pk=university_id)
            )
        except (University.DoesNotExist, ValidationError, ValueError) as exc:
            raise CommandError(f"University {university_id!r} does not exist.") from exc

    def _serialize_university(self, university: University) -> dict[str, Any]:
        return {
            "schema_version": EXPORT_SCHEMA_VERSION,
            "scope": "university_catalogue",
            "university": self._university(university),
            "media": [
                self._media(row) for row in university.media.all().order_by("sort_order", "id")
            ],
            "academic_units": [
                self._academic_unit(row)
                for row in university.academic_units.all().order_by("name_en", "id")
            ],
            "departments": [
                self._department(row)
                for row in university.departments.all().order_by("name_en", "id")
            ],
            "catalogue_sources": [
                self._catalogue_source(row)
                for row in university.catalogue_sources.all().order_by("received_at", "title", "id")
            ],
            "programs": [
                self._program(row)
                for row in university.programs.all().order_by("name_en", "slug_en", "id")
            ],
        }

    def _university(self, university: University) -> dict[str, Any]:
        return {
            "id": str(university.pk),
            **self._localized_names(university),
            **self._localized_slugs(university),
            **self._localized_descriptions(university),
            "website": university.website,
            "logo": university.logo.name if university.logo else "",
            "banner": university.banner.name if university.banner else "",
            "university_type": university.university_type,
            "is_yok_recognized": university.is_yok_recognized,
            "is_moe_approved": university.is_moe_approved,
            "is_moh_approved": university.is_moh_approved,
            "has_erasmus": university.has_erasmus,
            "has_dormitory": university.has_dormitory,
            "ranking_qs": university.ranking_qs,
            "ranking_the": university.ranking_the,
            "ranking_arwu": university.ranking_arwu,
            "ranking_urap": university.ranking_urap,
            "is_featured": university.is_featured,
            "listing_priority": university.listing_priority,
            "is_active": university.is_active,
            "city": self._city(university.city),
        }

    def _city(self, city) -> dict[str, Any]:
        province = city.province
        country = province.country
        return {
            "id": str(city.pk),
            **self._localized_names(city),
            **self._localized_slugs(city),
            "is_active": city.is_active,
            "province": {
                "id": str(province.pk),
                **self._localized_names(province),
                **self._localized_slugs(province),
                "is_active": province.is_active,
                "country": {
                    "id": str(country.pk),
                    "iso2": country.iso2,
                    "iso3": country.iso3,
                    **self._localized_names(country),
                    **self._localized_slugs(country),
                    "is_active": country.is_active,
                },
            },
        }

    def _media(self, row) -> dict[str, Any]:
        return {
            "id": str(row.pk),
            "image": row.image.name if row.image else "",
            "title": row.title,
            "sort_order": row.sort_order,
            "is_active": row.is_active,
        }

    def _academic_unit(self, row) -> dict[str, Any]:
        return {
            "id": str(row.pk),
            **self._localized_names(row),
            **self._localized_slugs(row),
            **self._localized_descriptions(row),
            "unit_type": row.unit_type,
            "is_active": row.is_active,
        }

    def _department(self, row) -> dict[str, Any]:
        return {
            "id": str(row.pk),
            **self._localized_names(row),
            **self._localized_slugs(row),
            **self._localized_descriptions(row),
            "is_active": row.is_active,
        }

    def _catalogue_source(self, row) -> dict[str, Any]:
        return {
            "id": str(row.pk),
            "title": row.title,
            "file": row.file.name if row.file else "",
            "received_at": row.received_at.isoformat(),
            "academic_year": self._named_reference(row.academic_year),
            "valid_from": self._date(row.valid_from),
            "valid_until": self._date(row.valid_until),
            "notes": row.notes,
        }

    def _program(self, program) -> dict[str, Any]:
        language_rows = program.instruction_language_rows.all().order_by(
            "-is_primary", "language__name_en", "id"
        )
        offerings = program.offerings.all().order_by(
            "academic_year__name_en", "semester__name_en", "id"
        )
        return {
            "id": str(program.pk),
            **self._localized_names(program),
            **self._localized_slugs(program),
            **self._localized_descriptions(program),
            "internal_notes": program.internal_notes,
            "academic_unit": self._reference(program.academic_unit),
            "department": self._reference(program.department),
            "degree": program.degree,
            "thesis_type": program.thesis_type,
            "study_mode": program.study_mode,
            "duration_months": program.duration_months,
            "legacy_duration_years": program.duration,
            "legacy_program_language": self._language(program.program_language),
            "listing_priority": program.listing_priority,
            "is_active": program.is_active,
            "instruction_languages": [self._instruction_language(row) for row in language_rows],
            "offerings": [self._offering(row) for row in offerings],
        }

    def _instruction_language(self, row) -> dict[str, Any]:
        return {
            "id": str(row.pk),
            "language": self._language(row.language),
            "percentage": self._decimal(row.percentage),
            "is_primary": row.is_primary,
        }

    def _language(self, language) -> dict[str, Any] | None:
        if language is None:
            return None
        return {
            "id": str(language.pk),
            **self._localized_names(language),
            **self._localized_slugs(language),
            **self._localized_descriptions(language),
            "is_active": language.is_active,
        }

    def _offering(self, offering) -> dict[str, Any]:
        return {
            "id": str(offering.pk),
            "academic_year": self._named_reference(offering.academic_year),
            "semester": self._named_reference(offering.semester),
            "fee_basis": offering.fee_basis,
            "currency": offering.currency,
            "tuition": self._decimal(offering.tuition),
            "tuition_discount_percentage": self._decimal(offering.tuition_discount_percentage),
            "tuition_discounted": self._decimal(offering.tuition_discounted),
            "cash_discount_percentage": self._decimal(offering.cash_discount_percentage),
            "tuition_cash": self._decimal(offering.tuition_cash),
            "tuition_annual_installment": self._decimal(offering.tuition_annual_installment),
            "deposit": self._decimal(offering.deposit),
            "preparatory_tuition": self._decimal(offering.preparatory_tuition),
            "preparation_included": offering.preparation_included,
            "quota": offering.quota,
            "deadline": self._date(offering.deadline),
            "valid_from": self._date(offering.valid_from),
            "valid_until": self._date(offering.valid_until),
            "notes": offering.notes,
            "source": self._source_reference(offering.source),
            "is_active": offering.is_active,
        }

    def _reference(self, value) -> dict[str, Any] | None:
        if value is None:
            return None
        return {
            "id": str(value.pk),
            **self._localized_names(value),
            **self._localized_slugs(value),
        }

    def _source_reference(self, value) -> dict[str, Any] | None:
        if value is None:
            return None
        return {"id": str(value.pk), "title": value.title}

    def _named_reference(self, value) -> dict[str, Any] | None:
        if value is None:
            return None
        return {"id": str(value.pk), **self._localized_names(value)}

    def _localized_names(self, value) -> dict[str, str]:
        return {f"name_{lang}": getattr(value, f"name_{lang}", "") for lang in LOCALIZED_LANGUAGES}

    def _localized_slugs(self, value) -> dict[str, str]:
        return {f"slug_{lang}": getattr(value, f"slug_{lang}", "") for lang in LOCALIZED_LANGUAGES}

    def _localized_descriptions(self, value) -> dict[str, str]:
        return {
            f"description_{lang}": getattr(value, f"description_{lang}", "")
            for lang in LOCALIZED_LANGUAGES
        }

    def _decimal(self, value) -> str | None:
        return None if value is None else format(value, "f")

    def _date(self, value) -> str | None:
        return None if value is None else value.isoformat()
