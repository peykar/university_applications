# Applicant finalization — technical design

Status: BASELINED

## Design mapping

- Canonical service is the Lead conversion/finalization service.
- Treat validation + Student creation + approved document copy + Lead transition
  as one workflow transaction boundary.
- UI is an Agent action from Applicant context.
- See ADR-001.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
