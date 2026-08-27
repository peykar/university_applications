# Email and notification templates — technical design

Status: BASELINED

## Design mapping

- Keep base-domain configuration environment-driven.
- Email preview registry is a development/admin verification surface.
- Supported language behavior follows project i18n settings.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
