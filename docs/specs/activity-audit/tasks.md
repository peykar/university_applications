# Activity and audit — tasks

Status: BASELINED

The current implementation predates formal SDD. Existing behavior is treated as
baseline subject to the gap report.

- [x] Extract established intended behavior into `AUD` requirements.
- [x] Record current technical design.
- [ ] Resolve any `AUD` findings marked `SPEC GAP` or `CODE GAP` in
      `docs/spec-code-gap-report.md`.
- [ ] For the next behavioral change, add requirement IDs before implementation.
- [ ] Update traceability after each implementation change.
- [ ] Run `make format` and `make check`.

## CHG-0013 — localized structured Activity rendering

- [x] `AUD-008` Add a centralized read-time Activity description renderer.
- [x] `AUD-008` Store structured metadata for predefined Activity producers.
- [x] `AUD-008` Render Agent Activity descriptions in the active interface language.
- [x] `AUD-008` Add/compile FA/TR/AR translations for predefined Activity sentences.
- [x] `AUD-009` Preserve and localize recognized legacy Activity description shapes.
- [x] `AUD-009` Preserve unknown/free-form descriptions verbatim.
- [x] `AUD-008`, `AUD-009` Add regression tests and update traceability/docs.
- [ ] Run `make format` and `make check` in the project environment.

## UI-0010 — cohesive RTL Activity timeline

- [x] `AUD-010` Keep Activity actor/date metadata adjacent to the event heading.
- [x] `AUD-010` Use logical start alignment so the compact metadata stack follows
      LTR/RTL direction naturally.
- [x] `AUD-010` Add bidi-safe presentation for Activity descriptions, actor names,
      and structured old/new audit values.
- [x] `AUD-010` Add structural regression coverage and update traceability/docs.
- [ ] Run `make format` and `make check` in the project environment.

