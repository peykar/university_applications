# FEAT-0006 — University catalogue v2

Status: APPROVED / SPECIFIED
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

Not implemented. This record authorizes the task plan; code changes are a
separate implementation step.
