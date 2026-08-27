# Student management — technical design

Status: BASELINED

## Design mapping

- Model: `Student`; source relation exposed by Lead conversion.
- Reusable documents: `StudentDocument`.
- Student is the required parent for formal Applications.
- See ADR-001 and ADR-005.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
