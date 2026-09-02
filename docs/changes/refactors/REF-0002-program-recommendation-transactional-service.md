# REF-0002 — Program recommendation transactional service

Status: IMPLEMENTED

## Request

Resolve G-001 in `docs/spec-code-gap-report.md` by moving Agent program
recommendation orchestration out of the Agent view and into an explicit domain
service without changing user-visible behavior.

## Governing requirements

- `PRG-002` — active Agent-scoped recommendation workflow.
- `PRG-003` — optional customer-understandable reason.
- `PRG-004` — agent source and suggesting user attribution.
- `PRG-005` — preserve existing user-created program-level interest.
- `PRG-006` — customer-visible activity and Applicant-scoped system message.
- `PRG-009` — active Program and active University constraint.

`PRG-007` remains implemented by the existing removal endpoint; recommendation
removal is intentionally outside this refactor's service boundary.

## Result

- Added `recommend_program(...)` in `apps/leads/services/recommendations.py`.
- Added an explicit `transaction.atomic` boundary for creation of the agent
  recommendation, customer-visible `PROGRAM_SUGGESTED` activity, and structured
  `PROGRAM_RECOMMENDED` system message.
- Moved duplicate/user-interest behavior and recommendation update behavior from
  `apps/agents/views.py` into the service.
- Added defensive rejection of finalized/closed Leads and inactive
  Program/University records inside the domain service while retaining the
  existing view-level guards and 404 behavior.
- Kept automatic/system-generated recommendation behavior disabled.
- Added named service-level regression tests and updated structural tests so the
  service, not the view, is the expected owner of recommendation side effects.

## User-visible behavior

No intentional behavior change. Existing success/info messages and redirects are
preserved for created, updated, already-recommended, and customer-added cases.

## Verification

Run `make format` and `make check`. If the delivery environment cannot resolve
locked dependencies, run the full gate in the normal development environment
and treat that as the release gate.
