# Activity and audit — technical design

Status: BASELINED

## Design mapping

- Model: `LeadActivity` with type, description, metadata and visibility flag.
- Shared recorder lives under Lead services/activity.
- Agent Activity page is separate from compact Applicant Overview.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
