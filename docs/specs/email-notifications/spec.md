# Email and notification templates

Status: ACTIVE
Version: 1.1

## Goal

Define TurkDemy's outgoing email contract for authentication and business workflow notifications.
Email is reserved for meaningful confirmation, required action, communication, or lifecycle events;
routine internal state changes remain in-app.

## Requirements

MAIL-001 — Outgoing links MUST use the configured public site/base URL.

MAIL-002 — The superuser-only Email Preview Gallery MUST be the canonical registry/gallery for
outgoing email template types.

MAIL-003 — A new outgoing email type MUST be registered with representative sample data.

MAIL-004 — A registered outgoing email type MUST have previews for every supported project language.

MAIL-005 — Authentication emails MUST use the established branded/authentication email behavior.

MAIL-006 — Creating a customer Request MUST send a confirmation to the customer and, when the
Request has an Agent, notify active users of that Agent that a new Request is ready for review.

MAIL-007 — A human customer/Agent message MUST notify the opposite party by email without copying
the conversation body into the email.

MAIL-008 — A newly created Agent program recommendation MUST notify the customer.

MAIL-009 — Requesting replacement of a customer document MUST notify the customer and include the
review reason when one was supplied.

MAIL-010 — Finalizing or re-finalizing a Request MUST send the customer a customer-safe lifecycle
milestone notification.

MAIL-011 — Creating a formal draft Application MUST notify the customer and identify its program
and university.

MAIL-012 — A material Application status change MUST notify the customer of the new customer-safe
status and link to the Application.

MAIL-013 — Assigning a TODO to another Agent user MUST notify that assignee. Creating a TODO for
oneself MUST NOT generate a redundant assignment email.

MAIL-014 — Business email delivery MUST be scheduled with `transaction.on_commit` so email is not
sent for a database transaction that later rolls back.

MAIL-015 — Business email failure MUST NOT be used as a reason to roll back the already committed
domain transaction.

MAIL-016 — Customer business emails MUST use customer-facing terminology and direct localized
application/request links where a corresponding route exists.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and covered by appropriate
tests. Negative authorization and invalid-state paths are part of acceptance when relevant.

## Non-goals

This version does not define notification preferences/digests, scheduled TODO reminders, SLA
escalations, university-recipient email, admission-requirement email, or a persistent delivery
outbox/retry subsystem.
