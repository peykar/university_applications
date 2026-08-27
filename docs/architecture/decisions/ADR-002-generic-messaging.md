# ADR-002: Generic subject-scoped messaging

Status: Accepted

## Context

Admissions communication can concern an Applicant, Student, Application, and
future domain subjects. Lead-specific messaging models would duplicate behavior.

## Decision

Use generic `Conversation` with Agent, customer, ContentType/object subject and
generic Messages/Attachments. Store read state per conversation + user +
participant role.

## Consequences

- Applicant and Application pages reuse one messaging subsystem.
- Agent users have independent unread state.
- New subject types should integrate with the generic service rather than add a
  parallel messaging model.
