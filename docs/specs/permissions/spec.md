# Authorization and privacy

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for authorization and privacy.

## Requirements

PERM-001 — Customer entity access MUST be limited to records owned/managed by the
authenticated customer.

PERM-002 — Agent entity access MUST be resolved through active-Agent-scoped
querysets.

PERM-003 — A User's membership in another Agent MUST NOT expose that Agent's
records while a different Agent is active.

PERM-004 — Session Agent identifiers MUST be revalidated before use.

PERM-005 — Protected actions MAY require responsibility in addition to
organization membership; the spec for that action MUST say so explicitly.

PERM-006 — Unauthorized entity identifiers SHOULD produce privacy-safe behavior
that does not disclose cross-customer/cross-Agent existence.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
