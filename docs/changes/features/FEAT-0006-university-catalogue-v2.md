# FEAT-0006 — University catalogue v2

Status: IMPLEMENTED / LOCAL VERIFICATION REQUIRED
Classification: FEATURE
Date: 2026-08-29

## Request

Align TurkDemy catalogue modelling with real university programme/tuition sheets
provided to education agents.

## Evidence reviewed

The supplied archive contains 2025–2027 university PDF/XLSX programme and
pricing lists. Observed dimensions include faculty/school/institute groupings,
mixed instruction languages, distance learning, fractional programme duration,
standard/discounted/cash/deposit pricing, preparatory fees, commercial
footnotes, and source-specific price terminology.

## Decision

Approve Catalogue v2 requirements `CAT-007` through `CAT-024` while preserving
`CAT-001` through `CAT-006`. Keep Program/ProgramOffering as the core boundary;
do not implement a generic pricing engine or admission requirements in this
feature.

## Artifacts

- `docs/specs/catalogue/spec.md` v2.0
- `docs/specs/catalogue/design.md` v2.0
- `docs/specs/catalogue/tasks.md` v2.0
- `docs/specs/catalogue/traceability.md` v2.0
- `docs/architecture/decisions/ADR-006-university-catalogue-v2.md`

## Implementation status

Implemented in the Catalogue v2 delivery. Canonical structures are live while
legacy single-language and whole-year duration fields remain as compatibility
bridges. Existing databases must generate/apply schema migrations and then run
`uv run python manage.py backfill_catalogue_v2` before deprecated readers are
removed in a later change. Admission requirements remain deferred by CAT-024.

## 2026-08-29 formatting follow-up

Resolved the two Catalogue v2 Ruff violations found by the local `make format` run:
`ProgramOfferingAdminForm` now declares its editable `ModelForm` fields explicitly (DJ007),
and `ProgramInstructionLanguage.Meta.constraints` is annotated as `ClassVar` (RUF012).
No catalogue behavior or SDD requirement changed.
