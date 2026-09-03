from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils.text import slugify

from apps.core.audit import get_system_user
from apps.universities.models import (
    AcademicUnit,
    AcademicUnitType,
    AcademicYear,
    Currency,
    DegreeType,
    Department,
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramLanguage,
    ProgramOffering,
    StudyMode,
    ThesisType,
    University,
    UniversityCatalogueSource,
)

SCHEMA_VERSION = 2
LOCALIZED_FIELDS = ("en", "fa", "tr", "ar")


class Command(BaseCommand):
    help = (
        "Import or update the programmes for one existing University from a "
        "TurkDemy university-programs JSON file and bind imported offerings to "
        "one UniversityCatalogueSource."
    )

    def add_arguments(self, parser):
        parser.add_argument("university_id", help="UUID of the target University")
        parser.add_argument(
            "university_catalogue_source_id",
            help="UUID of a UniversityCatalogueSource owned by the target University",
        )
        parser.add_argument("program_file", help="Path to a university-programs JSON file")

    def handle(self, *args, **options):
        university = self._get_university(options["university_id"])
        source = self._get_source(options["university_catalogue_source_id"], university=university)
        payload = self._load_payload(Path(options["program_file"]))
        self._validate_payload(payload)

        with transaction.atomic():
            result = self._import_payload(payload, university=university, source=source)

        self.stdout.write(
            self.style.SUCCESS(
                "University programme import complete. "
                f"Academic units created={result['academic_units_created']}, "
                f"updated={result['academic_units_updated']}; "
                f"Departments created={result['departments_created']}, "
                f"updated={result['departments_updated']}; "
                f"Programs created={result['programs_created']}, "
                f"updated={result['programs_updated']}; "
                f"Offerings created={result['offerings_created']}, "
                f"updated={result['offerings_updated']}."
            )
        )

    def _get_university(self, university_id: str) -> University:
        try:
            return University.objects.get(pk=university_id)
        except (University.DoesNotExist, ValidationError, ValueError) as exc:
            raise CommandError(f"University {university_id!r} does not exist.") from exc

    def _get_source(self, source_id: str, *, university: University) -> UniversityCatalogueSource:
        try:
            source = UniversityCatalogueSource.objects.select_related("university").get(
                pk=source_id
            )
        except (UniversityCatalogueSource.DoesNotExist, ValidationError, ValueError) as exc:
            raise CommandError(f"UniversityCatalogueSource {source_id!r} does not exist.") from exc
        if source.university_id != university.id:
            raise CommandError(
                "UniversityCatalogueSource must belong to the University supplied "
                "as the first argument."
            )
        return source

    def _load_payload(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise CommandError(f"Program file does not exist: {path}")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise CommandError("Program file must be UTF-8 encoded JSON.") from exc
        except json.JSONDecodeError as exc:
            raise CommandError(
                f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}: {exc.msg}"
            ) from exc
        if not isinstance(raw, dict):
            raise CommandError("Program file root must be a JSON object.")
        return raw

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        schema_version = payload.get("schema_version")
        if schema_version != SCHEMA_VERSION:
            raise CommandError(
                f"Unsupported schema_version {schema_version!r}; expected {SCHEMA_VERSION}."
            )

        academic_units = self._expect_list(payload, "academic_units", default=[])
        departments = self._expect_list(payload, "departments", default=[])
        programs = self._expect_list(payload, "programs")
        if not programs:
            raise CommandError("Program file must contain at least one program.")

        unit_slugs = self._validate_reference_rows(
            academic_units, section="academic_units", allowed_types=set(AcademicUnitType.values)
        )
        department_slugs = self._validate_reference_rows(
            departments, section="departments", allowed_types=None
        )

        seen_program_slugs: set[str] = set()
        for index, raw_program in enumerate(programs):
            path = f"programs[{index}]"
            program = self._expect_object(raw_program, path)
            slug_en = self._required_text(program, "slug_en", path=path)
            if slug_en in seen_program_slugs:
                raise CommandError(f"Duplicate program slug_en {slug_en!r} in {path}.")
            seen_program_slugs.add(slug_en)
            self._required_text(program, "name_en", path=path)

            self._validate_choice(program, "degree", set(DegreeType.values), path=path)
            self._validate_choice(
                program,
                "study_mode",
                set(StudyMode.values),
                path=path,
                default=StudyMode.ON_CAMPUS,
            )
            thesis_type = program.get("thesis_type")
            if thesis_type not in (None, "") and thesis_type not in set(ThesisType.values):
                raise CommandError(
                    f"{path}.thesis_type must be one of {sorted(ThesisType.values)} or null."
                )

            duration_months = program.get("duration_months")
            if duration_months is not None and (
                isinstance(duration_months, bool)
                or not isinstance(duration_months, int)
                or duration_months <= 0
            ):
                raise CommandError(f"{path}.duration_months must be a positive integer or null.")
            listing_priority = program.get("listing_priority", 0)
            if isinstance(listing_priority, bool) or not isinstance(listing_priority, int):
                raise CommandError(f"{path}.listing_priority must be an integer.")
            self._validate_optional_text(program, "internal_notes", path=path)
            self._validate_optional_bool(program, "is_active", path=path)
            if "general_field" in program or "general_fields" in program:
                raise CommandError(
                    f"{path}.general_fields are TurkDemy-curated and must be assigned "
                    "manually after import verification; remove it from the import file."
                )

            unit_slug = program.get("academic_unit")
            if unit_slug is not None and unit_slug not in unit_slugs:
                raise CommandError(
                    f"{path}.academic_unit references unknown academic-unit slug {unit_slug!r}."
                )
            department_slug = program.get("department")
            if department_slug is not None and department_slug not in department_slugs:
                raise CommandError(
                    f"{path}.department references unknown department slug {department_slug!r}."
                )

            languages = self._expect_list(program, "instruction_languages", path=path)
            self._validate_languages(languages, path=f"{path}.instruction_languages")

            offerings = self._expect_list(program, "offerings", default=[], path=path)
            self._validate_offerings(offerings, path=f"{path}.offerings")

    def _validate_reference_rows(
        self,
        rows: list[Any],
        *,
        section: str,
        allowed_types: set[str] | None,
    ) -> set[str]:
        slugs: set[str] = set()
        for index, raw_row in enumerate(rows):
            path = f"{section}[{index}]"
            row = self._expect_object(raw_row, path)
            slug_en = self._required_text(row, "slug_en", path=path)
            self._required_text(row, "name_en", path=path)
            if slug_en in slugs:
                raise CommandError(f"Duplicate slug_en {slug_en!r} in {section}.")
            slugs.add(slug_en)
            self._validate_optional_bool(row, "is_active", path=path)
            if allowed_types is not None:
                self._validate_choice(row, "unit_type", allowed_types, path=path)
        return slugs

    def _validate_languages(self, rows: list[Any], *, path: str) -> None:
        if not rows:
            raise CommandError(f"{path} must contain at least one language.")

        seen_slugs: set[str] = set()
        primary_count = 0
        percentages: list[Decimal | None] = []
        for index, raw_row in enumerate(rows):
            row_path = f"{path}[{index}]"
            row = self._expect_object(raw_row, row_path)
            slug = self._required_text(row, "slug", path=row_path)
            self._required_text(row, "name_en", path=row_path)
            if slug in seen_slugs:
                raise CommandError(f"Duplicate language slug {slug!r} in {path}.")
            seen_slugs.add(slug)
            self._validate_optional_bool(row, "is_primary", path=row_path)
            if row.get("is_primary", False):
                primary_count += 1
            percentages.append(
                self._decimal_or_none(row.get("percentage"), path=f"{row_path}.percentage")
            )

        if primary_count > 1:
            raise CommandError(f"{path} may identify at most one primary language.")

        known = [value for value in percentages if value is not None]
        if known:
            if len(known) != len(percentages):
                raise CommandError(
                    f"{path}: when one language percentage is supplied, all language "
                    "percentages must be supplied."
                )
            for value in known:
                if value < Decimal("0") or value > Decimal("100"):
                    raise CommandError(f"{path}: language percentages must be between 0 and 100.")
            if sum(known, Decimal("0")) != Decimal("100"):
                raise CommandError(f"{path}: language percentages must total exactly 100.")

    def _validate_offerings(self, rows: list[Any], *, path: str) -> None:
        seen_keys: set[tuple[str, str]] = set()
        for index, raw_row in enumerate(rows):
            row_path = f"{path}[{index}]"
            row = self._expect_object(raw_row, row_path)
            academic_year = self._required_text(row, "academic_year", path=row_path)
            intake_name = self._required_text(row, "intake", path=row_path)
            key = (academic_year, intake_name)
            if key in seen_keys:
                raise CommandError(
                    f"Duplicate offering for academic_year={academic_year!r}, "
                    f"intake={intake_name!r} in {path}."
                )
            seen_keys.add(key)

            fees = self._expect_list(row, "fees", path=row_path)
            for fee_index, raw_fee in enumerate(fees):
                fee_path = f"{row_path}.fees[{fee_index}]"
                fee = self._expect_object(raw_fee, fee_path)
                self._validate_choice(fee, "fee_type", set(OfferingFeeType.values), path=fee_path)
                self._validate_choice(fee, "currency", set(Currency.values), path=fee_path)
                self._validate_choice(fee, "basis", set(FeeBasis.values), path=fee_path)
                amount = self._decimal_or_none(fee.get("amount"), path=f"{fee_path}.amount")
                percentage = self._decimal_or_none(
                    fee.get("percentage"), path=f"{fee_path}.percentage"
                )
                if amount is None and percentage is None:
                    raise CommandError(
                        f"{fee_path} must provide at least one of amount or percentage."
                    )
                if amount is not None and amount < 0:
                    raise CommandError(f"{fee_path}.amount cannot be negative.")
                if percentage is not None and (
                    percentage < Decimal("0") or percentage > Decimal("100")
                ):
                    raise CommandError(f"{fee_path}.percentage must be between 0 and 100.")
                self._validate_optional_text(fee, "label", path=fee_path)
                self._validate_optional_text(fee, "language", path=fee_path)
                self._validate_optional_text(fee, "notes", path=fee_path)

            self._validate_optional_bool(row, "preparation_included", path=row_path)
            self._validate_optional_bool(row, "is_active", path=row_path)
            quota = row.get("quota")
            if quota is not None and (
                isinstance(quota, bool) or not isinstance(quota, int) or quota < 0
            ):
                raise CommandError(f"{row_path}.quota must be a non-negative integer or null.")
            for field in ("deadline", "valid_from", "valid_until"):
                self._date_or_none(row.get(field), path=f"{row_path}.{field}")
            valid_from = self._date_or_none(row.get("valid_from"), path=f"{row_path}.valid_from")
            valid_until = self._date_or_none(row.get("valid_until"), path=f"{row_path}.valid_until")
            if valid_from and valid_until and valid_until < valid_from:
                raise CommandError(f"{row_path}.valid_until cannot be earlier than valid_from.")

    def _import_payload(
        self,
        payload: dict[str, Any],
        *,
        university: University,
        source: UniversityCatalogueSource,
    ) -> dict[str, int]:
        actor = get_system_user()
        counters = {
            "academic_units_created": 0,
            "academic_units_updated": 0,
            "departments_created": 0,
            "departments_updated": 0,
            "programs_created": 0,
            "programs_updated": 0,
            "offerings_created": 0,
            "offerings_updated": 0,
        }

        academic_units: dict[str, AcademicUnit] = {}
        for raw_row in self._expect_list(payload, "academic_units", default=[]):
            row = self._expect_object(raw_row, "academic_units[]")
            slug_en = str(row["slug_en"])
            academic_unit_defaults: dict[str, Any] = self._localized_defaults(row)
            academic_unit_defaults.update(
                {
                    "unit_type": row["unit_type"],
                    "description_en": str(row.get("description_en") or ""),
                    "description_fa": str(row.get("description_fa") or ""),
                    "description_tr": str(row.get("description_tr") or ""),
                    "description_ar": str(row.get("description_ar") or ""),
                    "is_active": bool(row.get("is_active", True)),
                }
            )
            unit, created = self._upsert(
                AcademicUnit,
                lookup={"university": university, "slug_en": slug_en},
                defaults=academic_unit_defaults,
                actor=actor,
            )
            academic_units[slug_en] = unit
            counters["academic_units_created" if created else "academic_units_updated"] += 1

        departments: dict[str, Department] = {}
        for raw_row in self._expect_list(payload, "departments", default=[]):
            row = self._expect_object(raw_row, "departments[]")
            slug_en = str(row["slug_en"])
            department_defaults: dict[str, Any] = self._localized_defaults(row)
            department_defaults.update(
                {
                    "description_en": str(row.get("description_en") or ""),
                    "description_fa": str(row.get("description_fa") or ""),
                    "description_tr": str(row.get("description_tr") or ""),
                    "description_ar": str(row.get("description_ar") or ""),
                    "is_active": bool(row.get("is_active", True)),
                }
            )
            department, created = self._upsert(
                Department,
                lookup={"university": university, "slug_en": slug_en},
                defaults=department_defaults,
                actor=actor,
            )
            departments[slug_en] = department
            counters["departments_created" if created else "departments_updated"] += 1

        for raw_program in self._expect_list(payload, "programs"):
            row = self._expect_object(raw_program, "programs[]")
            program, created = self._upsert_program(
                row,
                university=university,
                academic_units=academic_units,
                departments=departments,
                actor=actor,
            )
            counters["programs_created" if created else "programs_updated"] += 1
            self._sync_languages(program, row["instruction_languages"], actor=actor)

            for raw_offering in self._expect_list(row, "offerings", default=[]):
                offering_row = self._expect_object(raw_offering, "offerings[]")
                offering_created = self._upsert_offering(
                    program,
                    offering_row,
                    source=source,
                    actor=actor,
                )
                counters["offerings_created" if offering_created else "offerings_updated"] += 1

        return counters

    def _upsert_program(
        self,
        row: dict[str, Any],
        *,
        university: University,
        academic_units: dict[str, AcademicUnit],
        departments: dict[str, Department],
        actor: Any,
    ) -> tuple[Program, bool]:
        academic_unit_slug = row.get("academic_unit")
        department_slug = row.get("department")

        defaults: dict[str, Any] = self._localized_defaults(row)
        defaults.update(
            {
                "description_en": str(row.get("description_en") or ""),
                "description_fa": str(row.get("description_fa") or ""),
                "description_tr": str(row.get("description_tr") or ""),
                "description_ar": str(row.get("description_ar") or ""),
                "academic_unit": academic_units.get(str(academic_unit_slug))
                if academic_unit_slug
                else None,
                "department": departments.get(str(department_slug)) if department_slug else None,
                "degree": row["degree"],
                "thesis_type": row.get("thesis_type") or None,
                "study_mode": row.get("study_mode", StudyMode.ON_CAMPUS),
                "duration_months": row.get("duration_months"),
                "listing_priority": int(row.get("listing_priority", 0)),
                "is_active": bool(row.get("is_active", True)),
            }
        )
        if "internal_notes" in row:
            defaults["internal_notes"] = str(row.get("internal_notes") or "")

        # GeneralField is intentionally absent from importer defaults. It is a
        # TurkDemy-curated classification assigned only after catalogue verification.
        # New Programs therefore start unmapped, while re-imports preserve any
        # existing manual Program.general_fields assignments.

        source_slug_en = str(row["slug_en"])
        university_prefix = f"{university.slug_en}-"
        legacy_canonical_slug_en = (
            source_slug_en
            if source_slug_en.startswith(university_prefix)
            else f"{university_prefix}{source_slug_en}"
        )
        language_rows = self._expect_list(row, "instruction_languages")
        ordered_languages = sorted(
            language_rows,
            key=lambda language: (
                not bool(language.get("is_primary", False)),
                str(language.get("slug") or language.get("name_en") or ""),
            ),
        )
        language_tokens = [
            str(language.get("slug") or "").strip()
            for language in ordered_languages
            if str(language.get("slug") or "").strip()
        ]
        degree_token = str(row["degree"])
        thesis_type = row.get("thesis_type") or None
        thesis_token = ""
        if thesis_type == ThesisType.THESIS:
            thesis_token = "thesis"
        elif thesis_type == ThesisType.NON_THESIS:
            thesis_token = "non-thesis"

        academic_unit = defaults["academic_unit"]
        department = defaults["department"]
        hierarchy_tokens = [
            str(getattr(academic_unit, "slug_en", "") or "").strip(),
            str(getattr(department, "slug_en", "") or "").strip(),
        ]
        structured_parts = [
            university.slug_en,
            *[token for token in hierarchy_tokens if token],
            slugify(str(row["name_en"])),
            degree_token,
        ]
        previous_structured_parts = [
            university.slug_en,
            slugify(str(row["name_en"])),
            degree_token,
        ]
        if thesis_token:
            structured_parts.append(thesis_token)
            previous_structured_parts.append(thesis_token)
        structured_parts.extend(language_tokens)
        previous_structured_parts.extend(language_tokens)
        structured_slug_en = "-".join(part for part in structured_parts if part)
        previous_structured_slug_en = "-".join(part for part in previous_structured_parts if part)

        # ``slug_en`` in schema-v2 input is the stable source identity for
        # re-imports. Program.slug_en itself is now rebuilt from mutable
        # structured display data, so a renamed Program cannot be found from
        # its current canonical slug alone. Reconstruct the canonical slug that
        # the stable source identity would have produced and include it as a
        # transition/upsert candidate.
        source_identity_tail = source_slug_en.removeprefix(university_prefix)
        suffix_tokens = [*language_tokens]
        if thesis_token:
            suffix_tokens.insert(0, thesis_token)
        suffix_tokens.insert(0, degree_token)
        for token in reversed(suffix_tokens):
            suffix = f"-{token}"
            if source_identity_tail.endswith(suffix):
                source_identity_tail = source_identity_tail[: -len(suffix)]
        source_identity_parts = [
            university.slug_en,
            *[token for token in hierarchy_tokens if token],
            source_identity_tail,
            degree_token,
        ]
        previous_source_identity_parts = [
            university.slug_en,
            source_identity_tail,
            degree_token,
        ]
        if thesis_token:
            source_identity_parts.append(thesis_token)
            previous_source_identity_parts.append(thesis_token)
        source_identity_parts.extend(language_tokens)
        previous_source_identity_parts.extend(language_tokens)
        source_identity_canonical_slug_en = "-".join(part for part in source_identity_parts if part)
        previous_source_identity_canonical_slug_en = "-".join(
            part for part in previous_source_identity_parts if part
        )

        matches = Program.objects.filter(university=university).filter(
            Q(slug_en=structured_slug_en)
            | Q(slug_en=previous_structured_slug_en)
            | Q(slug_en=source_identity_canonical_slug_en)
            | Q(slug_en=previous_source_identity_canonical_slug_en)
            | Q(slug_en=legacy_canonical_slug_en)
            | Q(slug_en=source_slug_en)
        )
        if matches.count() > 1:
            raise CommandError(
                f"Multiple existing Program rows match source/canonical slug "
                f"{source_slug_en!r}/{structured_slug_en!r}. Resolve duplicates before importing."
            )
        instance = matches.first()
        created = instance is None
        if instance is None:
            instance = Program(university=university, created_by=actor)
        for field, value in defaults.items():
            setattr(instance, field, value)
        instance.slug_en = structured_slug_en
        instance.updated_by = actor
        instance.full_clean()
        instance.save()
        return instance, created

    def _sync_languages(self, program: Program, raw_rows: Any, *, actor: Any) -> None:
        rows = self._expect_list({"rows": raw_rows}, "rows")
        # The JSON file is authoritative for the instruction-language composition
        # of each imported Program. Recreate the through rows so updates cannot
        # temporarily combine old and new percentages and violate CAT-010.
        program.instruction_language_rows.all().delete()
        for raw_row in rows:
            row = self._expect_object(raw_row, "instruction_languages[]")
            language = self._get_or_create_language(row, actor=actor)
            percentage = self._decimal_or_none(
                row.get("percentage"), path="instruction_languages[].percentage"
            )
            association = ProgramInstructionLanguage(
                program=program,
                language=language,
                percentage=percentage,
                is_primary=bool(row.get("is_primary", False)),
                created_by=actor,
                updated_by=actor,
            )
            association.full_clean()
            association.save()

    def _get_or_create_language(self, row: dict[str, Any], *, actor: Any) -> ProgramLanguage:
        slug = str(row["slug"])
        language = ProgramLanguage.objects.filter(slug_en=slug).first()
        if language is None:
            language = ProgramLanguage(
                slug_en=slug,
                name_en=str(row["name_en"]),
                name_fa=str(row.get("name_fa") or ""),
                name_tr=str(row.get("name_tr") or ""),
                name_ar=str(row.get("name_ar") or ""),
                slug_fa=str(row.get("slug_fa") or ""),
                slug_tr=str(row.get("slug_tr") or ""),
                slug_ar=str(row.get("slug_ar") or ""),
                created_by=actor,
                updated_by=actor,
            )
            language.full_clean()
            language.save()
        return language

    def _upsert_offering(
        self,
        program: Program,
        row: dict[str, Any],
        *,
        source: UniversityCatalogueSource,
        actor: Any,
    ) -> bool:
        academic_year = self._get_or_create_academic_year(str(row["academic_year"]), actor=actor)
        intake_name = str(row["intake"])
        intake = self._get_or_create_intake(
            intake_name, academic_year=academic_year, university=program.university, actor=actor
        )
        lookup = {
            "program": program,
            "academic_year": academic_year,
            "intake": intake,
            "source": source,
        }
        matches = ProgramOffering.objects.filter(**lookup)
        if matches.count() > 1:
            raise CommandError(
                "Multiple existing ProgramOffering rows match the import key "
                f"program={program.slug_en!r}, academic_year={academic_year.name_en!r}, "
                f"intake={intake.name_en!r}, source={source.id}. Resolve duplicates first."
            )
        offering = matches.first()
        created = offering is None
        if offering is None:
            offering = ProgramOffering(**lookup, created_by=actor)

        offering.preparation_included = bool(row.get("preparation_included", False))
        offering.quota = row.get("quota")
        offering.deadline = self._date_or_none(row.get("deadline"), path="offering.deadline")
        offering.valid_from = self._date_or_none(row.get("valid_from"), path="offering.valid_from")
        offering.valid_until = self._date_or_none(
            row.get("valid_until"), path="offering.valid_until"
        )
        offering.notes = str(row.get("notes") or "")
        offering.is_active = bool(row.get("is_active", True))
        offering.updated_by = actor
        offering.full_clean()
        offering.save()
        self._sync_structured_fees(offering, row, actor=actor)
        return created

    def _get_or_create_academic_year(self, name: str, *, actor: Any) -> AcademicYear:
        academic_year = AcademicYear.objects.filter(name_en=name).first()
        if academic_year is None:
            academic_year = AcademicYear(name_en=name, created_by=actor, updated_by=actor)
            academic_year.full_clean()
            academic_year.save()
        return academic_year

    def _get_or_create_intake(
        self,
        name: str,
        *,
        academic_year: AcademicYear,
        university: University,
        actor: Any,
    ) -> Intake:
        intake = Intake.objects.filter(
            university=university, academic_year=academic_year, name_en=name
        ).first()
        if intake is None:
            intake = Intake(
                university=university,
                academic_year=academic_year,
                name_en=name,
                created_by=actor,
                updated_by=actor,
            )
            intake.full_clean()
            intake.save()
        return intake

    def _sync_structured_fees(
        self, offering: ProgramOffering, row: dict[str, Any], *, actor: Any
    ) -> None:
        fee_rows = self._expect_list(row, "fees", path="offering")
        OfferingFee.objects.filter(offering=offering).delete()
        for index, raw_fee in enumerate(fee_rows):
            fee_row = self._expect_object(raw_fee, f"offering.fees[{index}]")
            amount = self._decimal_or_none(
                fee_row.get("amount"), path=f"offering.fees[{index}].amount"
            )
            percentage = self._decimal_or_none(
                fee_row.get("percentage"), path=f"offering.fees[{index}].percentage"
            )
            language = None
            language_slug = fee_row.get("language")
            if language_slug:
                language = ProgramLanguage.objects.filter(slug_en=str(language_slug)).first()
                if language is None:
                    raise CommandError(f"Unknown fee language slug {language_slug!r}.")
            fee = OfferingFee(
                offering=offering,
                fee_type=str(fee_row["fee_type"]),
                label=str(fee_row.get("label") or ""),
                language=language,
                currency=str(fee_row["currency"]),
                amount=amount,
                percentage=percentage,
                basis=str(fee_row["basis"]),
                notes=str(fee_row.get("notes") or ""),
                created_by=actor,
                updated_by=actor,
            )
            fee.full_clean()
            fee.save()

    def _upsert(
        self,
        model: Any,
        *,
        lookup: dict[str, Any],
        defaults: dict[str, Any],
        actor: Any,
    ) -> tuple[Any, bool]:
        matches = model.objects.filter(**lookup)
        if matches.count() > 1:
            raise CommandError(
                f"Multiple existing {model.__name__} rows match import key {lookup!r}. "
                "Resolve duplicates before importing."
            )
        instance = matches.first()
        created = instance is None
        if instance is None:
            instance = model(**lookup, created_by=actor)
        for field, value in defaults.items():
            setattr(instance, field, value)
        instance.updated_by = actor
        instance.full_clean()
        instance.save()
        return instance, created

    def _localized_defaults(self, row: dict[str, Any]) -> dict[str, str]:
        values: dict[str, str] = {}
        for language in LOCALIZED_FIELDS:
            name_field = f"name_{language}"
            slug_field = f"slug_{language}"
            values[name_field] = str(row.get(name_field) or "")
            if language == "en":
                values[slug_field] = str(row[slug_field])
            else:
                values[slug_field] = str(row.get(slug_field) or "")
        return values

    def _expect_list(
        self,
        obj: dict[str, Any],
        key: str,
        *,
        default: list[Any] | None = None,
        path: str = "root",
    ) -> list[Any]:
        value = obj.get(key, default)
        if not isinstance(value, list):
            raise CommandError(f"{path}.{key} must be a JSON array.")
        return value

    def _expect_object(self, value: Any, path: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise CommandError(f"{path} must be a JSON object.")
        return value

    def _required_text(self, obj: dict[str, Any], key: str, *, path: str) -> str:
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip():
            raise CommandError(f"{path}.{key} must be a non-empty string.")
        return value.strip()

    def _validate_choice(
        self,
        obj: dict[str, Any],
        key: str,
        allowed: set[str],
        *,
        path: str,
        default: str | None = None,
    ) -> None:
        value = obj.get(key, default)
        if value not in allowed:
            raise CommandError(f"{path}.{key} must be one of {sorted(allowed)}.")

    def _validate_optional_text(self, obj: dict[str, Any], key: str, *, path: str) -> None:
        if key in obj and obj[key] is not None and not isinstance(obj[key], str):
            raise CommandError(f"{path}.{key} must be a JSON string or null.")

    def _validate_optional_bool(self, obj: dict[str, Any], key: str, *, path: str) -> None:
        if key in obj and not isinstance(obj[key], bool):
            raise CommandError(f"{path}.{key} must be a JSON boolean.")

    def _decimal_or_none(self, value: Any, *, path: str) -> Decimal | None:
        if value in (None, ""):
            return None
        if isinstance(value, bool):
            raise CommandError(f"{path} must be a decimal value or null.")
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise CommandError(f"{path} must be a decimal value or null.") from exc

    def _required_decimal(self, obj: dict[str, Any], key: str, *, path: str) -> Decimal:
        value = self._decimal_or_none(obj.get(key), path=f"{path}.{key}")
        if value is None:
            raise CommandError(f"{path}.{key} is required.")
        return value

    def _date_or_none(self, value: Any, *, path: str) -> date | None:
        if value in (None, ""):
            return None
        if not isinstance(value, str):
            raise CommandError(f"{path} must be an ISO date (YYYY-MM-DD) or null.")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise CommandError(f"{path} must be an ISO date (YYYY-MM-DD) or null.") from exc
