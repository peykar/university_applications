# Identity & authentication — technical design

Status: BASELINED

## Design mapping

- `django-allauth` remains the authentication integration.
- Canonical connection-management UI: `/accounts/settings/sign-in-methods/`.
- Google and Telegram connection use allauth `process="connect"`.
- Direct email login uses allauth login-by-code routes.
- Provider buttons are conditional on provider configuration.
- See existing `docs/authentication.md` for provider configuration details.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
