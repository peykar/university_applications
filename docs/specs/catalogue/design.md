# University and program catalogue — technical design

Status: BASELINED

## Design mapping

- Models live in `apps.universities`.
- Offering-level filters must constrain the same Offering row when combining
  intake-specific conditions.
- Slug-based public navigation is preferred where existing routes support it.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
