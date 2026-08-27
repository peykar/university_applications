# Agent organizations and active workspace — technical design

Status: BASELINED

## Design mapping

- Canonical resolver: `apps.agents.services.context.resolve_active_agent()`.
- Session key: `active_agent_id`.
- Agent query helpers derive Leads/Students/Applications/Conversations from the
  resolved Agent.
- Switch POST validates membership and only preserves organization-neutral routes.
- See ADR-003.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
