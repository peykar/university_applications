# Generic messaging — technical design

Status: BASELINED

## Design mapping

- Models: Conversation, Message, MessageAttachment,
  ConversationParticipantState.
- Generic subject uses ContentType + object UUID.
- Reuse messaging service for new subject types.
- See ADR-002.

## Cross-cutting constraints

- Follow canonical rules in `docs/product/business-rules.md`.
- Follow `docs/architecture/permissions.md`.
- Preserve auditability for state-changing workflows.
- Prefer service-layer workflow logic over duplicated view logic.

## Architecture decisions

Consult the ADRs under `docs/architecture/decisions/` when this capability
touches Lead→Student conversion, generic messaging, active Agent context,
program-interest/Application boundaries, or document layers.
