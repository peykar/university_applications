# Navigation and workspace information architecture — technical design

Status: BASELINED

## Design mapping

- Shared workspace base templates provide L2 navigation.
- Applicant/Application header/nav partials provide L3.
- Agent desktop shell may use a wider content container than public catalogue.
- See `docs/architecture/navigation.md`.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
