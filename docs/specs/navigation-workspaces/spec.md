# Navigation and workspace information architecture

Status: BASELINED
Version: 1.1

## Goal

Define the established TurkDemy behavior for navigation and workspace information architecture.

## Requirements

NAV-001 — Global navigation MUST focus on public discovery plus workspace/account
entry rather than flattening private workflow links into the header.

NAV-002 — My TurkDemy and Agent workspace MUST remain distinct workspace contexts.

NAV-003 — Agent sidebar MUST expose Overview, Applicants, Applications, Messages
and active organization identity.

NAV-004 — Agent Applicant entity navigation MUST expose Overview, Profile, Programs,
Documents, Applications and Messages. Customer case navigation MUST follow the
customer Request abstraction defined by the Customer Requests capability.

NAV-005 — Application entity navigation MUST expose Overview, Requirements,
Documents, Activity and Messages.

NAV-006 — Similar labels at different navigation levels MUST preserve their
documented scope.

NAV-007 — Applicant Overview SHOULD summarize and link to focused areas rather
than duplicate full Messages/Documents/Programs panels.

NAV-008 — Workspace/entity navigation MUST remain usable on mobile through the
established responsive behavior.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
