# Program interests and recommendations — tasks

Status: BASELINED

The current implementation predates formal SDD. Existing behavior is treated as
baseline subject to the gap report.

- [x] Extract established intended behavior into `PRG` requirements.
- [x] Record current technical design.
- [x] Resolve G-001 program recommendation service/atomicity code gap via
      `REF-0002`.
- [x] Move recommendation duplicate/update/create orchestration from Agent view
      into `apps.leads.services.recommendations.recommend_program`.
- [x] Make new recommendation interest/activity/system-message creation atomic.
- [x] Add named tests for `PRG-002` through `PRG-006` and defensive lifecycle
      validation.
- [x] Update PRG traceability for the REF-0002 implementation.
- [ ] Resolve any remaining `PRG` findings marked `SPEC GAP` or `CODE GAP` in
      `docs/spec-code-gap-report.md`.
- [ ] For the next behavioral change, add requirement IDs before implementation.
- [ ] Update traceability after each implementation change.
- [ ] Run `make format` and `make check` for each delivery.
