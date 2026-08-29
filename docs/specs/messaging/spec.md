# Generic messaging

Status: BASELINED
Version: 1.1

## Goal

Define the established TurkDemy behavior for generic messaging.

## Requirements

MSG-001 — Agent/customer communication MUST use generic subject-scoped
Conversation rather than Lead-specific message models.

MSG-002 — Conversation MUST identify Agent, customer and generic subject.

MSG-003 — Messages MUST identify sender and sender role.

MSG-004 — Messages MAY contain attachments.

MSG-005 — Read state MUST be independent per Conversation + User + participant
role.

MSG-006 — Different Agent users MUST have independent unread state.

MSG-007 — Applicant Messages MUST be scoped to the Applicant; Application
Messages MUST be scoped to the Application; workspace Messages MUST act as inbox.

MSG-008 — Conversation access MUST respect customer ownership and active-Agent
authorization for the subject.

MSG-009 — Subject-scoped messaging MUST NOT make an otherwise valid customer Request inaccessible when the subject has no Agent yet. No Conversation may be created without the required Agent/customer pair; customer message composition MUST remain unavailable until that pair exists, and direct send attempts MUST fail safely without a server error.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
