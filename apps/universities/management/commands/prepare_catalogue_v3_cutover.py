from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from apps.core.audit import get_system_user
from apps.universities.models import (
    FeeBasis,
    Intake,
    OfferingFee,
    OfferingFeeType,
    Program,
    ProgramInstructionLanguage,
    ProgramOffering,
)


@dataclass
class CutoverCounts:
    durations: int = 0
    languages: int = 0
    intakes: int = 0
    fees: int = 0


class Command(BaseCommand):
    help = (
        "Backfill missing Catalogue v3 data from still-present Catalogue v2 database "
        "columns before generating/applying the destructive v3-only migration."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform all checks/backfill logic in a transaction and roll it back.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        program_table = Program._meta.db_table
        offering_table = ProgramOffering._meta.db_table
        legacy_semester_table = "universities_semester"

        program_columns = self._columns(program_table)
        offering_columns = self._columns(offering_table)
        tables = set(connection.introspection.table_names())

        has_legacy_program = {"duration", "program_language_id"}.issubset(program_columns)
        legacy_offering_columns = {
            "semester_id",
            "fee_basis",
            "currency",
            "tuition",
            "tuition_discount_percentage",
            "tuition_discounted",
            "cash_discount_percentage",
            "tuition_cash",
            "tuition_annual_installment",
            "deposit",
            "pre_school_fees",
        }
        has_legacy_offering = legacy_offering_columns.issubset(offering_columns)

        if not has_legacy_program and not has_legacy_offering:
            self.stdout.write(
                self.style.SUCCESS(
                    "No Catalogue v2 database columns were detected; no cutover backfill is needed."
                )
            )
            return

        actor = get_system_user()
        counts = CutoverCounts()

        if has_legacy_program:
            self._backfill_programs(program_table, actor=actor, counts=counts)

        if has_legacy_offering:
            if legacy_semester_table not in tables:
                raise CommandError(
                    "Legacy ProgramOffering columns exist but the universities_semester table "
                    "is missing. Restore/inspect the database before applying the "
                    "v3-only migration."
                )
            self._backfill_offerings(
                offering_table,
                legacy_semester_table,
                actor=actor,
                counts=counts,
            )

        unresolved = ProgramOffering.objects.filter(intake_id__isnull=True).count()
        if unresolved:
            raise CommandError(
                f"Catalogue v3 cutover is not safe: {unresolved} ProgramOffering row(s) "
                "still have no Intake. Resolve them before generating/applying migrations."
            )

        if options["dry_run"]:
            transaction.set_rollback(True)
            mode = "Dry run complete; changes were rolled back."
        else:
            mode = "Cutover backfill complete."

        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} durations={counts.durations}, languages={counts.languages}, "
                f"intakes={counts.intakes}, fees={counts.fees}."
            )
        )

    def _columns(self, table: str) -> set[str]:
        tables = set(connection.introspection.table_names())
        if table not in tables:
            return set()
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(cursor, table)
        return {column.name for column in description}

    def _fetch(self, sql: str) -> list[tuple[Any, ...]]:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return list(cursor.fetchall())

    def _backfill_programs(self, table: str, *, actor: Any, counts: CutoverCounts) -> None:
        quote = connection.ops.quote_name
        rows = self._fetch(
            f"SELECT {quote('id')}, {quote('duration')}, {quote('program_language_id')} "
            f"FROM {quote(table)}"
        )
        for program_id, duration, language_id in rows:
            program = Program.objects.get(pk=program_id)
            if program.duration_months is None and duration is not None:
                program.duration_months = int(duration) * 12
                program.updated_by = actor
                program.save(update_fields=("duration_months", "updated_by", "updated_at"))
                counts.durations += 1
            if language_id and not program.instruction_language_rows.exists():
                ProgramInstructionLanguage.objects.create(
                    program=program,
                    language_id=language_id,
                    is_primary=True,
                    created_by=actor,
                    updated_by=actor,
                )
                counts.languages += 1

    def _backfill_offerings(
        self,
        table: str,
        semester_table: str,
        *,
        actor: Any,
        counts: CutoverCounts,
    ) -> None:
        quote = connection.ops.quote_name
        semester_rows = self._fetch(
            f"SELECT {quote('id')}, {quote('name_en')}, {quote('name_fa')}, "
            f"{quote('name_tr')}, {quote('name_ar')} FROM {quote(semester_table)}"
        )
        semester_names = {
            str(row[0]): {
                "name_en": str(row[1] or ""),
                "name_fa": str(row[2] or ""),
                "name_tr": str(row[3] or ""),
                "name_ar": str(row[4] or ""),
            }
            for row in semester_rows
        }

        fields = (
            "id",
            "intake_id",
            "semester_id",
            "fee_basis",
            "currency",
            "tuition",
            "tuition_discount_percentage",
            "tuition_discounted",
            "cash_discount_percentage",
            "tuition_cash",
            "tuition_annual_installment",
            "deposit",
            "pre_school_fees",
        )
        rows = self._fetch(
            f"SELECT {', '.join(quote(field) for field in fields)} FROM {quote(table)}"
        )
        for row in rows:
            legacy = dict(zip(fields, row, strict=True))
            offering = ProgramOffering.objects.select_related(
                "program__university", "academic_year"
            ).get(pk=legacy["id"])

            if legacy["intake_id"] is None:
                semester_id = legacy["semester_id"]
                names = semester_names.get(str(semester_id)) if semester_id else None
                if not names or not names["name_en"]:
                    raise CommandError(
                        f"Offering {offering.pk} has no canonical Intake and its legacy "
                        "Semester cannot be resolved."
                    )
                matching_intakes = Intake.objects.filter(
                    university=offering.program.university,
                    academic_year=offering.academic_year,
                    name_en=names["name_en"],
                )
                match_count = matching_intakes.count()
                if match_count > 1:
                    raise CommandError(
                        f"Offering {offering.pk} maps to {match_count} canonical Intakes "
                        f"named {names['name_en']!r}; resolve the duplicate Intakes before "
                        "running the cutover."
                    )
                intake = matching_intakes.first()
                if intake is None:
                    intake = Intake.objects.create(
                        university=offering.program.university,
                        academic_year=offering.academic_year,
                        name_en=names["name_en"],
                        name_fa=names["name_fa"],
                        name_tr=names["name_tr"],
                        name_ar=names["name_ar"],
                        created_by=actor,
                        updated_by=actor,
                    )
                offering.intake = intake
                offering.updated_by = actor
                offering.save(update_fields={"intake", "updated_by", "updated_at"})
                counts.intakes += 1

            basis = str(legacy["fee_basis"] or FeeBasis.ANNUAL)
            currency = str(legacy["currency"] or "USD")
            fee_specs = (
                (
                    OfferingFeeType.TUITION,
                    legacy["tuition"],
                    None,
                    basis,
                ),
                (
                    OfferingFeeType.DISCOUNTED_TUITION,
                    legacy["tuition_discounted"],
                    legacy["tuition_discount_percentage"],
                    basis,
                ),
                (
                    OfferingFeeType.CASH_PAYMENT,
                    legacy["tuition_cash"],
                    legacy["cash_discount_percentage"],
                    basis,
                ),
                (
                    OfferingFeeType.INSTALLMENT_TOTAL,
                    legacy["tuition_annual_installment"],
                    None,
                    basis,
                ),
                (
                    OfferingFeeType.DEPOSIT,
                    legacy["deposit"],
                    None,
                    FeeBasis.ONE_TIME,
                ),
                (
                    OfferingFeeType.PREPARATORY,
                    legacy["pre_school_fees"],
                    None,
                    basis,
                ),
            )
            for fee_type, amount, percentage, fee_basis in fee_specs:
                decimal_amount = Decimal(str(amount)) if amount is not None else None
                decimal_percentage = Decimal(str(percentage)) if percentage is not None else None
                if decimal_amount is None and decimal_percentage is None:
                    continue
                existing_types = {fee_type}
                if fee_type == OfferingFeeType.CASH_PAYMENT:
                    existing_types.add(OfferingFeeType.ADVANCE_PAYMENT)
                if offering.fees.filter(fee_type__in=existing_types).exists():
                    continue
                fee = OfferingFee(
                    offering=offering,
                    fee_type=fee_type,
                    currency=currency,
                    amount=decimal_amount,
                    percentage=decimal_percentage,
                    basis=fee_basis,
                    created_by=actor,
                    updated_by=actor,
                )
                fee.full_clean()
                fee.save()
                counts.fees += 1
