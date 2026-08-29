# Navigation and workspace information architecture

Status: BASELINED
Version: 1.3

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

NAV-009 — The shared site footer MUST use the customer-facing **My TurkDemy** workspace concept rather than obsolete **Students / Dashboard / Profile** terminology. For authenticated users it MUST link to **My Requests** and customer **Messages**; for unauthenticated users the same footer group MAY provide the Login entry.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.

NAV-010 — The customer workspace navigation MUST expose **My Requests**, **Messages**, **Get Help**, and the optional **Message us on WhatsApp** action on mobile without clipping any item off-screen. Labels MAY wrap within their navigation cell, and the layout MUST adapt when the optional WhatsApp action is absent.
