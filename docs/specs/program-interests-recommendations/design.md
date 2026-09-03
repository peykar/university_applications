# Program interests and recommendations — technical design

Status: BASELINED

## Design mapping

- Model: `LeadProgramInterest`.
- Program-level and offering-level uniqueness are database-constrained.
- Agent recommendation endpoints live in Agent workspace and scope Lead through
  active Agent.
- Recommendation search queries Program/University names and only admits active
  Program records whose University is active.
- `apps.leads.services.recommendations.recommend_program(...)` is the domain
  boundary for creating/updating an Agent recommendation.
- The service owns preservation of existing user-created interests, update/no-op
  handling for existing Agent recommendations, attribution, and creation side
  effects.
- New recommendation creation runs under `transaction.atomic`: the
  `LeadProgramInterest`, customer-visible `PROGRAM_SUGGESTED` LeadActivity, and
  structured `PROGRAM_RECOMMENDED` system Message commit together or roll back
  together.
- The Agent view owns HTTP concerns only: Agent scoping, request parsing,
  catalogue lookup, user-facing flash messages, and redirect behavior.
- Recommendation reasons remain structured data: `LeadProgramInterest.suggestion_reason`
  is rendered on customer program surfaces, and the corresponding
  `LeadActivity.metadata["suggestion_reason"]` is rendered with the customer and
  Agent PROGRAM_SUGGESTED activity presentation. The reason is not duplicated
  into the activity description string.
- UI-0009 gives those rendered reasons a shared bidi-aware advisor-note treatment; this is presentation-only and does not alter recommendation/activity/message persistence.
- Automatic/system-generated program recommendations remain disabled.
- Recommendation removal remains a separate Agent endpoint and is not part of
  REF-0002's creation/update transaction boundary.
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
