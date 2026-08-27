# Applicant management — technical design

Status: BASELINED

## Design mapping

- `Lead` is the provisional Applicant aggregate.
- Customer ownership starts from `Lead.user`.
- Agent access starts from active-Agent-scoped Lead queryset.
- Agent edits use the shared applicant activity recorder.
- Entity-level navigation is implemented by applicant header/nav partials.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
