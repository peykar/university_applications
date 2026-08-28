# CHG-0003 — Finalization program selection is optional

Status: IMPLEMENTED

## Decision

During Lead finalization, the responsible Agent may select zero or more discussed
program interests. Selecting no programs does not block finalization: the Student
is still created/reused and the Lead becomes finalized, with zero draft Applications
created by that operation.

For every interest that is selected, the existing requirements remain unchanged:
it must resolve to an active concrete ProgramOffering and it creates one linked
DRAFT Application in the same atomic finalization transaction.

## Affected requirements

- `FIN-007`–`FIN-009`
- `APP-002`, `APP-003`, `APP-006`
- `BR-FIN-005`

## Verification

Covered by Lead finalization service tests, Agent finalization UI contract tests,
SDD traceability validation, and the project verification pipeline.
