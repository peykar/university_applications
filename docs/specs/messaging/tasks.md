# Generic messaging — tasks

Status: BASELINED

The current implementation predates formal SDD. Existing behavior is treated as
baseline subject to the gap report.

- [x] Extract established intended behavior into `MSG` requirements.
- [x] Record current technical design.
- [ ] Resolve any `MSG` findings marked `SPEC GAP` or `CODE GAP` in
      `docs/spec-code-gap-report.md`.
- [ ] For the next behavioral change, add requirement IDs before implementation.
- [ ] Update traceability after each implementation change.
- [ ] Run `make format` and `make check`.
- [x] `MSG-009` Guard customer Request messaging until the subject has an Agent while preserving the Conversation invariant.

- [x] `MSG-T10` — Add structured system-event persistence plus active-locale rendering with legacy
      body fallback (`MSG-010`, `CHG-0010`).
- [x] `MSG-T11` — Convert current workflow system-message producers and all product message
      presentation surfaces to `localized_body`; add runtime localization/compatibility regressions.
