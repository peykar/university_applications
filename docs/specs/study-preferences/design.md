# Applicant study preferences — technical design

Status: BASELINED

## Design mapping

- Stored in `LeadPreference` one-to-one with Lead.
- Catalogue relations use M2M where implemented.
- Degree/university type codes are validated against catalogue choices.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
