# Program interests and recommendations — technical design

Status: BASELINED

## Design mapping

- Model: `LeadProgramInterest`.
- Program-level and offering-level uniqueness are database-constrained.
- Agent recommendation endpoints live in Agent workspace and scope Lead through
  active Agent.
- Recommendation search queries Program/University names.
- Side effects: LeadActivity + generic system message.
- See ADR-004.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
