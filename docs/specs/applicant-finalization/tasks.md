# Applicant finalization — tasks

Status: BASELINED

The current implementation predates formal SDD. Existing behavior is treated as
baseline subject to the gap report.

- [x] Extract established intended behavior into `FIN` requirements.
- [x] Record current technical design.
- [ ] Resolve any `FIN` findings marked `SPEC GAP` or `CODE GAP` in
      `docs/spec-code-gap-report.md`.
- [ ] For the next behavioral change, add requirement IDs before implementation.
- [ ] Update traceability after each implementation change.
- [ ] Run `make format` and `make check`.

## CHANGE: discussed programs become draft applications during finalization

- [x] `FIN-007` Show customer-added and Agent-suggested discussed programs in the finalization UI and allow zero or more selections.
- [x] `FIN-008` Require a concrete active offering for every selected program.
- [x] `FIN-009` Create linked DRAFT Applications in the same atomic finalization transaction.
- [x] Keep Agent Workspace as the supported interactive finalization path; discussed-program selection is optional.
- [x] Add/update automated tests and requirement-level traceability.

## CHANGE: full-page Create Student Record conversion

- [x] `FIN-010` Replace the finalization modal with the full-page `Create Student Record` action.
- [x] `FIN-002` Prefill editable Student fields from the Lead and validate submitted Student data.
- [x] `FIN-011`–`FIN-014` Add explicit Lead-document selection, default verified documents on, approve selected unverified documents, and transfer only selected documents.
- [x] `FIN-007`–`FIN-009` List all discussed programs, allow zero-or-more choices, and require an active offering for each checked program.
- [x] Remove persistent `LeadProgramInterest.converted_application` / `source_interest` coupling.
- [x] `FIN-015` Preserve conversion selections on validation failure.
- [x] `FIN-016` Keep all conversion database mutations under the atomic service boundary.
- [x] `FIN-017` Preserve the existing LeadDocument → StudentDocument conversion bridge only.
- [x] Add/update tests and SDD traceability.
