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
## Subjects awaiting Agent assignment

`Conversation` continues to require both Agent and customer. Callers that present an optional messaging surface for an Agent-less Lead MUST treat the conversation as unavailable rather than weakening that invariant or creating a partial Conversation. Customer Request views use empty message state until assignment; send attempts are rejected safely.


## Locale-aware system events

`Message.event_type` and `Message.event_data` are the canonical representation for newly generated
workflow/system messages covered by `MSG-010`. `Message.body` is retained as an English fallback
snapshot so deleted references, unknown future event types, and pre-structured historical rows remain
readable.

`apps.messaging.services.render_system_message_body()` renders known event types under the active
Django locale. Referenced Programs and Universities are resolved by stable IDs and use their
`localized_name` values at render time. User-authored reason text remains verbatim. Document event
data stores the stable document-type choice value and resolves its translated label at render time.

`Message.localized_body` is the presentation boundary used by conversation/detail/inbox templates
and view-model previews. Non-system messages and historical system rows with no `event_type` return
the stored `body` unchanged. Current producers use structured events for program recommendations,
document replacement upload/request, and Applicant finalization.

The repository does not check in generated Django migrations. Operators use the normal project
`makemigrations`/`migrate` workflow to add the two Message columns on existing databases.
