# Email and notification templates

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for email and notification templates.

## Requirements

MAIL-001 — Outgoing links MUST use the configured public site/base URL.

MAIL-002 — The superuser-only Email Preview Gallery MUST be the canonical
registry/gallery for outgoing email template types.

MAIL-003 — A new outgoing email type MUST be registered with representative
sample data.

MAIL-004 — A registered outgoing email type MUST have previews for every
supported project language.

MAIL-005 — Authentication emails MUST use the established branded/authentication
email template behavior.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
