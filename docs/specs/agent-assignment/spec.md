# Agent responsibility and lifecycle

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for agent responsibility and lifecycle.

## Requirements

ASN-001 — All authorized users of a Lead's Agent MAY see the Lead; assignment
MUST NOT be used as the organization visibility boundary.

ASN-002 — Active Leads MAY be assigned/reassigned only to an active user of the
same Agent.

ASN-003 — Assignment MUST set active workflow status to `assigned`; absence of an
assignee MUST result in `new`.

ASN-004 — Assignment/reassignment MUST create auditable activity.

ASN-005 — An Agent user MAY use Assign to me to take responsibility.

ASN-006 — Only the currently responsible Agent user MAY finalize the Lead.

ASN-007 — Closing MAY record a reason/actor/time; reopening MUST restore
`assigned` or `new` according to current assignment.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
