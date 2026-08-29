# FEAT-0007 — Normalized university programme JSON import

Status: IMPLEMENTED / LOCAL VERIFICATION REQUIRED
Date: 2026-08-30

## Request

Provide one deterministic management command that imports normalized programme
data for an already selected University and UniversityCatalogueSource. Source
PDF/XLSX interpretation is intentionally separate: those source files can be
converted into the documented JSON format first, then imported with the same
stable command.

## Implementation

Added:

```text
python manage.py import_programs_for_university \
  <university-id> <university-catalogue-source-id> <program-file.json>
```

The command validates that the source belongs to the University, validates
schema version 1, then atomically upserts AcademicUnits, optional Departments,
Programs, canonical instruction-language rows, and ProgramOfferings.

Stable keys:

- AcademicUnit: University + `slug_en`
- Department: University + `slug_en`
- Program: University + `slug_en`
- ProgramOffering: Program + AcademicYear + Semester + supplied source

Program instruction-language composition is synchronized exactly for Programs
present in the JSON. Rows absent from the JSON are not deleted/deactivated. All
imported offerings are bound to the supplied source.

## Documentation

- `docs/university-program-json-import.md`
- `docs/examples/university-programs-v1.json`
- Catalogue SDD v2.1, CAT-025 through CAT-030

## Verification

Added `tests/test_university_program_json_import.py` covering create/import,
idempotent updates, source-University ownership, invalid percentage rollback,
and duplicate Program slug rejection. Repository-level syntax/SDD checks are
run in the delivery environment; full `make check` is required locally.
