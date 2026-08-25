# Agent workspace

TurkDemy has a dedicated operational workspace for users attached to an active
`Agent` through `Agent.users`.

## Routes

- `/agent/` — operational overview.
- `/agent/applicants/` — agent-scoped applicants/leads.
- `/agent/messages/` — conversation inbox with per-user unread counts.
- `/agent/applications/` — customer program requests plus formal applications associated with the agent.

The routes are inside `i18n_patterns`, so deployed URLs include the active
language prefix (for example `/en/agent/`).

## Access control

Normal agent users only see records whose `agent` belongs to
`request.user.agents`. Formal applications with no explicit `Application.agent`
also fall back to `Application.student.agent`. Superusers may access all active
agents. A logged-in user with no active agent membership receives HTTP 403.

This scoping is applied in the view querysets; it is not only a template/UI
restriction.

## Workflow

The overview surfaces new applicants, unread customer messages, applications
needing action, recommendation requests, and unverified lead documents.

From an applicant page an agent can review profile information, study
preferences, documents and program interests; read the conversation; reply as
staff; and update the applicant workflow status.

From an application page an agent can review the student/program/application
documents and update the formal application status.

Message read receipts are per user, so opening a conversation clears unread
messages for that agent user without incorrectly marking them read for every
other user in the agent company.
