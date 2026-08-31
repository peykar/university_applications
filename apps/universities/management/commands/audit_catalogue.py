from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.universities.models import (
    AcademicUnit,
    Department,
    OfferingFeeType,
    Program,
    ProgramOffering,
    University,
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    university: str
    object_type: str
    object_id: str
    message: str


class Command(BaseCommand):
    help = "Audit the persisted Catalogue v3 data without modifying it."

    PROVENANCE_TERMS = (
        "rasa",
        "imported from",
        "source:",
        "source file",
        "normalized json",
        "workbook",
        "mapping",
    )

    def add_arguments(self, parser):
        parser.add_argument("--json-output", type=Path)
        parser.add_argument("--csv-output", type=Path)
        parser.add_argument(
            "--fail-on-errors",
            action="store_true",
            help="Exit non-zero when ERROR findings exist (the audit is always read-only).",
        )

    def handle(self, *args, **options):
        findings: list[Finding] = []
        universities = list(University.objects.order_by("name_en", "id"))
        programs = list(
            Program.objects.select_related("university", "academic_unit", "department")
            .prefetch_related("instruction_language_rows__language")
            .order_by("university__name_en", "name_en", "id")
        )
        offerings = list(
            ProgramOffering.objects.select_related(
                "program__university", "academic_year", "intake", "source"
            )
            .prefetch_related("fees")
            .order_by("program__university__name_en", "program__name_en", "id")
        )

        self._audit_universities(universities, findings)
        self._audit_programs(programs, findings)
        self._audit_offerings(offerings, findings)
        self._audit_unused_hierarchy(findings)

        summary = self._summary(universities, programs, offerings, findings)
        self._write_human(summary, findings)
        if options["json_output"]:
            self._write_json(options["json_output"], summary, findings)
        if options["csv_output"]:
            self._write_csv(options["csv_output"], findings)
        if options["fail_on_errors"] and summary["findings"]["ERROR"]:
            raise SystemExit(1)

    def _add(self, findings, severity, code, obj, message):
        university = ""
        if isinstance(obj, University):
            university = obj.name_en
        elif hasattr(obj, "university"):
            university = obj.university.name_en
        elif hasattr(obj, "program"):
            university = obj.program.university.name_en
        findings.append(
            Finding(severity, code, university, obj.__class__.__name__, str(obj.pk), message)
        )

    def _audit_universities(self, universities, findings):
        for locale in ("en", "fa", "tr", "ar"):
            slug_groups = defaultdict(list)
            for university in universities:
                slug = str(getattr(university, f"slug_{locale}", "") or "").strip()
                if slug:
                    slug_groups[slug].append(university)
            for slug, group in slug_groups.items():
                if len(group) > 1:
                    ids = ", ".join(str(university.pk) for university in group)
                    for university in group:
                        self._add(
                            findings,
                            "ERROR",
                            "UNI_DUPLICATE_SLUG",
                            university,
                            f"Duplicate {locale} university slug {slug!r}; IDs: {ids}",
                        )
        for university in universities:
            for locale in ("en", "fa", "tr", "ar"):
                if not str(getattr(university, f"name_{locale}", "") or "").strip():
                    self._add(
                        findings,
                        "WARNING",
                        "UNI_MISSING_NAME",
                        university,
                        f"Missing {locale} name.",
                    )
                if not str(getattr(university, f"slug_{locale}", "") or "").strip():
                    self._add(
                        findings,
                        "ERROR",
                        "UNI_MISSING_SLUG",
                        university,
                        f"Missing {locale} slug.",
                    )
                if not str(getattr(university, f"description_{locale}", "") or "").strip():
                    self._add(
                        findings,
                        "WARNING",
                        "UNI_MISSING_DESCRIPTION",
                        university,
                        f"Missing {locale} description.",
                    )
            if not university.logo:
                self._add(
                    findings,
                    "WARNING",
                    "UNI_MISSING_LOGO",
                    university,
                    "No university logo.",
                )
            if not university.banner:
                self._add(
                    findings,
                    "WARNING",
                    "UNI_MISSING_BANNER",
                    university,
                    "No university banner.",
                )
            if not university.website:
                self._add(
                    findings,
                    "WARNING",
                    "UNI_MISSING_WEBSITE",
                    university,
                    "No university website.",
                )

    def _audit_programs(self, programs, findings):
        identities = defaultdict(list)
        for program in programs:
            rows = list(program.instruction_language_rows.all())
            for locale in ("en", "fa", "tr", "ar"):
                if not str(getattr(program, f"name_{locale}", "") or "").strip():
                    self._add(
                        findings,
                        "WARNING",
                        "PROGRAM_MISSING_NAME",
                        program,
                        f"Missing {locale} name.",
                    )
                if not str(getattr(program, f"slug_{locale}", "") or "").strip():
                    self._add(
                        findings,
                        "ERROR",
                        "PROGRAM_MISSING_SLUG",
                        program,
                        f"Missing {locale} public slug.",
                    )
            if not rows:
                self._add(
                    findings,
                    "ERROR",
                    "PROGRAM_NO_LANGUAGE",
                    program,
                    "No structured instruction language.",
                )
            else:
                primary_count = sum(1 for row in rows if row.is_primary)
                if primary_count != 1:
                    self._add(
                        findings,
                        "WARNING",
                        "PROGRAM_PRIMARY_LANGUAGE",
                        program,
                        f"Expected one primary language; found {primary_count}.",
                    )
                known = [row.percentage for row in rows if row.percentage is not None]
                if known and len(known) == len(rows) and sum(known, Decimal("0")) != Decimal("100"):
                    self._add(
                        findings,
                        "WARNING",
                        "PROGRAM_LANGUAGE_PERCENT",
                        program,
                        (
                            "Explicit instruction-language percentages total "
                            f"{sum(known, Decimal('0'))}%, not 100%."
                        ),
                    )
            if program.degree in ("master", "phd") and not program.thesis_type:
                self._add(
                    findings,
                    "WARNING",
                    "PROGRAM_MISSING_THESIS_TYPE",
                    program,
                    "Graduate program has no thesis type.",
                )
            if program.is_active and not program.offerings.filter(is_active=True).exists():
                self._add(
                    findings,
                    "ERROR",
                    "PROGRAM_NO_ACTIVE_OFFERING",
                    program,
                    "Active program has no active offering.",
                )
            for field in ("internal_notes",):
                value = str(getattr(program, field, "") or "").lower()
                # Internal provenance is expected; no finding here.
                # Kept explicit to document the public/internal boundary.
                _ = value
            lang_key = tuple(sorted(row.language_id for row in rows))
            identity = (
                program.university_id,
                program.academic_unit_id,
                program.department_id,
                program.name_en.strip().casefold(),
                program.degree,
                program.thesis_type or "",
                program.study_mode,
                lang_key,
            )
            identities[identity].append(program)
            for locale in ("en", "fa", "tr", "ar"):
                slug = str(getattr(program, f"slug_{locale}", "") or "")
                if slug.rsplit("-", 1)[-1].isdigit() and int(slug.rsplit("-", 1)[-1]) >= 2:
                    self._add(
                        findings,
                        "INFO",
                        "PROGRAM_NUMERIC_SLUG_TAIL",
                        program,
                        f"{locale} slug uses a numeric collision tail: {slug}",
                    )
        for group in identities.values():
            if len(group) > 1:
                ids = ", ".join(str(program.pk) for program in group)
                for program in group:
                    self._add(
                        findings,
                        "WARNING",
                        "PROGRAM_DUPLICATE_IDENTITY",
                        program,
                        f"Possible duplicate structured program identity; group IDs: {ids}",
                    )

    def _audit_offerings(self, offerings, findings):
        seen_keys = defaultdict(list)
        for offering in offerings:
            program = offering.program
            if offering.intake.university_id not in (None, program.university_id):
                self._add(
                    findings,
                    "ERROR",
                    "OFFERING_INTAKE_UNIVERSITY",
                    offering,
                    "Intake belongs to a different university.",
                )
            if offering.intake.academic_year_id != offering.academic_year_id:
                self._add(
                    findings,
                    "ERROR",
                    "OFFERING_INTAKE_YEAR",
                    offering,
                    "Intake academic year differs from offering academic year.",
                )
            if offering.is_active and not offering.source_id:
                self._add(
                    findings,
                    "WARNING",
                    "OFFERING_NO_SOURCE",
                    offering,
                    "Active offering has no catalogue source provenance link.",
                )
            if offering.source_id and offering.source.university_id != program.university_id:
                self._add(
                    findings,
                    "ERROR",
                    "OFFERING_SOURCE_UNIVERSITY",
                    offering,
                    "Catalogue source belongs to a different university.",
                )
            if (
                offering.source_id
                and offering.source.academic_year_id
                and offering.source.academic_year_id != offering.academic_year_id
            ):
                self._add(
                    findings,
                    "WARNING",
                    "OFFERING_SOURCE_YEAR",
                    offering,
                    "Catalogue source academic year differs from offering academic year.",
                )
            public_notes = str(offering.notes or "").lower()
            if public_notes and any(term in public_notes for term in self.PROVENANCE_TERMS):
                self._add(
                    findings,
                    "WARNING",
                    "OFFERING_PUBLIC_PROVENANCE",
                    offering,
                    "Public offering notes appear to contain import/provenance commentary.",
                )

            fees = [fee for fee in offering.fees.all() if fee.is_active]
            tuition = [
                fee
                for fee in fees
                if fee.fee_type in (OfferingFeeType.TUITION, OfferingFeeType.DISCOUNTED_TUITION)
                and fee.amount is not None
            ]
            if offering.is_active and not tuition:
                self._add(
                    findings,
                    "ERROR",
                    "OFFERING_NO_TUITION",
                    offering,
                    (
                        "Active offering has no active amount-bearing tuition fee; "
                        "Application creation is not ready."
                    ),
                )
            fee_keys = Counter(
                (
                    fee.fee_type,
                    fee.language_id,
                    fee.currency,
                    fee.basis,
                    fee.label.strip().casefold(),
                )
                for fee in fees
            )
            if any(count > 1 for count in fee_keys.values()):
                self._add(
                    findings,
                    "WARNING",
                    "OFFERING_DUPLICATE_FEE",
                    offering,
                    "Possible duplicate active structured fee rows.",
                )
            for fee in fees:
                if fee.amount is not None and fee.amount <= 0:
                    self._add(
                        findings,
                        "ERROR",
                        "FEE_NON_POSITIVE_AMOUNT",
                        offering,
                        f"{fee.get_fee_type_display()} has non-positive amount {fee.amount}.",
                    )
                if fee.notes and any(term in fee.notes.lower() for term in self.PROVENANCE_TERMS):
                    self._add(
                        findings,
                        "WARNING",
                        "FEE_PUBLIC_PROVENANCE",
                        offering,
                        (
                            f"{fee.get_fee_type_display()} notes appear to contain "
                            "import/provenance commentary."
                        ),
                    )
            list_fees = [
                fee
                for fee in fees
                if fee.fee_type == OfferingFeeType.TUITION and fee.amount is not None
            ]
            discounted = [
                fee
                for fee in fees
                if fee.fee_type == OfferingFeeType.DISCOUNTED_TUITION and fee.amount is not None
            ]
            if (
                list_fees
                and discounted
                and min(f.amount for f in discounted) > max(f.amount for f in list_fees)
            ):
                self._add(
                    findings,
                    "WARNING",
                    "FEE_DISCOUNT_ABOVE_LIST",
                    offering,
                    "Discounted tuition is greater than list tuition.",
                )
            key = (
                offering.program_id,
                offering.academic_year_id,
                offering.intake_id,
                offering.source_id,
            )
            seen_keys[key].append(offering)
        for group in seen_keys.values():
            if len(group) > 1:
                ids = ", ".join(str(offering.pk) for offering in group)
                for offering in group:
                    self._add(
                        findings,
                        "ERROR",
                        "OFFERING_DUPLICATE_KEY",
                        offering,
                        f"Duplicate Program + year + intake + source offering key; IDs: {ids}",
                    )

    def _audit_unused_hierarchy(self, findings):
        unused_units = AcademicUnit.objects.annotate(program_count=Count("programs")).filter(
            program_count=0, is_active=True
        )
        for unit in unused_units.select_related("university"):
            self._add(
                findings,
                "WARNING",
                "ACADEMIC_UNIT_UNUSED",
                unit,
                "Active academic unit is not used by any program.",
            )
        unused_departments = Department.objects.annotate(program_count=Count("programs")).filter(
            program_count=0, is_active=True
        )
        for department in unused_departments.select_related("university"):
            self._add(
                findings,
                "WARNING",
                "DEPARTMENT_UNUSED",
                department,
                "Active department is not used by any program.",
            )

    def _summary(self, universities, programs, offerings, findings):
        severity = Counter(f.severity for f in findings)
        fee_count = sum(offering.fees.count() for offering in offerings)
        language_count = sum(program.instruction_language_rows.count() for program in programs)
        return {
            "universities": len(universities),
            "programs": len(programs),
            "active_programs": sum(1 for p in programs if p.is_active),
            "offerings": len(offerings),
            "active_offerings": sum(1 for o in offerings if o.is_active),
            "fees": fee_count,
            "instruction_language_rows": language_count,
            "findings": {level: severity[level] for level in ("ERROR", "WARNING", "INFO")},
        }

    def _write_human(self, summary, findings):
        self.stdout.write("CATALOGUE AUDIT (read-only)")
        self.stdout.write("=" * 27)
        self.stdout.write(f"Universities: {summary['universities']}")
        self.stdout.write(f"Programs: {summary['programs']} ({summary['active_programs']} active)")
        self.stdout.write(
            f"Offerings: {summary['offerings']} ({summary['active_offerings']} active)"
        )
        self.stdout.write(f"Structured fees: {summary['fees']}")
        self.stdout.write(f"Instruction-language rows: {summary['instruction_language_rows']}")
        self.stdout.write("")
        finding_counts = ", ".join(
            f"{level}={summary['findings'][level]}" for level in ("ERROR", "WARNING", "INFO")
        )
        self.stdout.write("Findings: " + finding_counts)
        grouped = defaultdict(list)
        for finding in findings:
            grouped[finding.university or "(global)"].append(finding)
        for university in sorted(grouped):
            self.stdout.write("")
            self.stdout.write(university)
            for finding in grouped[university]:
                self.stdout.write(
                    f"  [{finding.severity}] {finding.code} "
                    f"{finding.object_type}:{finding.object_id} — {finding.message}"
                )

    def _write_json(self, path, summary, findings):
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"summary": summary, "findings": [asdict(f) for f in findings]}
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.stdout.write(f"JSON report: {path}")

    def _write_csv(self, path, findings):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "severity",
                    "code",
                    "university",
                    "object_type",
                    "object_id",
                    "message",
                ],
            )
            writer.writeheader()
            writer.writerows(asdict(f) for f in findings)
        self.stdout.write(f"CSV report: {path}")
