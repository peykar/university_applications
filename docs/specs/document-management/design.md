# Document management — technical design

Status: BASELINED

## Design mapping

- Lead: `LeadDocument`, `LeadDocumentVersion`, `LeadDocumentReviewHistory`.
- Student: `StudentDocument`.
- Application: `ApplicationDocument`.
- Keep review/version mutations in explicit workflow code.
- Requirements remain a separate concern; current Application Requirements UI
  derives only from existing data and is not a full requirements domain model.
- See ADR-005.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
