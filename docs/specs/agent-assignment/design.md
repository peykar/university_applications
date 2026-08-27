# Agent responsibility and lifecycle — technical design

Status: BASELINED

## Design mapping

- `Lead.assigned_to` stores responsibility.
- `Lead.save()` derives active new/assigned state.
- Assignment/status actions remain Agent-scoped.
- Finalization adds a responsibility restriction beyond visibility.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
