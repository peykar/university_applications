# Agent organizations and active workspace

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for agent organizations and active workspace.

## Requirements

AGT-001 — An Agent MUST represent an organization and MAY contain multiple users.

AGT-002 — A User MAY belong to multiple Agents.

AGT-003 — Agent workspace MUST operate in one active-Agent context.

AGT-004 — With one available Agent, the workspace MUST auto-select it.

AGT-005 — With multiple available Agents and no valid prior selection, the User
MUST explicitly choose an Agent.

AGT-006 — A stale/tampered active-Agent session value MUST be rejected and
revalidated against current memberships.

AGT-007 — Agent workspace sidebar MUST display active Agent name and logo or
fallback identity and expose organization switching when multiple Agents exist.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
