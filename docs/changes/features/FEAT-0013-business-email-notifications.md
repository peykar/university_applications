# FEAT-0013 — Business email notifications

Status: IMPLEMENTED

## Intent

Add transactional email notifications to the existing Request, messaging, recommendation,
document review, finalization, Application, and TODO flows without turning routine internal
state changes into email noise.

## SDD impact

Extends the `MAIL` capability. Every new outgoing type is registered in the canonical Email
Preview Gallery and is previewable for every supported language. Customer-facing messages use
customer terminology and direct links; internal implementation terms are not exposed unless the
customer UI already exposes that concept.

## Implemented events

- Request created: confirmation to customer and new-request notice to active Agent users.
- Human message: Agent → customer or customer → Agent users. Message body is not copied into email.
- Agent program recommendation: customer notification.
- Document replacement requested: customer action-required notification including review reason.
- Request finalized/re-finalized: customer milestone notification.
- Draft Application created: customer notification.
- Application status changed: customer notification.
- TODO assigned to a different Agent user: assignee notification.

## Deliberately deferred

Digests, notification preferences, due/overdue scheduled reminders, university-recipient email,
SLA/escalation email, delivery retry/outbox persistence, and admission-requirement email remain
future behavior and require their own SDD change.
