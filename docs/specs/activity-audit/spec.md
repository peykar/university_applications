# Activity and audit

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for activity and audit.

## Requirements

AUD-001 — Applicant data changes from customer and Agent edit workflows MUST be
recorded through shared normalization/audit behavior.

AUD-002 — Audit changes SHOULD store human-readable normalized old/new values
rather than raw foreign-key IDs when possible.

AUD-003 — Internal notes MUST remain private to Agent/staff users.

AUD-004 — Internal-note edits MUST preserve old/new values in structured
activity metadata.

AUD-005 — Full Applicant activity MUST be available to Agent users as a dedicated
audit page with filtering/pagination.

AUD-006 — Customer-visible events MUST be explicitly marked; internal events MUST
not be exposed to customers.

AUD-007 — Historical audit/version data MUST be preserved across workflow changes.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
