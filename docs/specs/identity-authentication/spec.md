# Identity & authentication

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for identity & authentication.

## Requirements

AUTH-001 — TurkDemy MUST support passwordless direct email authentication using
the established code flow.

AUTH-002 — TurkDemy MUST support configured Google and Telegram sign-in through
django-allauth.

AUTH-003 — Connecting a provider while authenticated MUST attach it to the
current User and MUST NOT silently merge a provider identity already owned by
another User.

AUTH-004 — The Sign-in methods page MUST prevent removal of the User's last
usable sign-in method.

AUTH-005 — A trusted Google verified email matching an existing account MUST
preserve that account's existing local identity/data and password usability.

AUTH-006 — Authentication routes under `/accounts/` remain unlocalized so OAuth
callback URLs are stable.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
