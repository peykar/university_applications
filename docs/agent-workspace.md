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

## Default lead assignment

Default lead ownership is configured through the environment and Django
settings, not through a database model.

Set the Agent UUID in `.env`:

```env
DEFAULT_LEAD_AGENT_ID=3fa85f64-5717-4562-b3fc-2c963f66afa6
```

`turkdemy.settings.base` exposes this as `settings.DEFAULT_LEAD_AGENT_ID`.

- If it is set and points to an active Agent, a new lead with no explicit
  agent is assigned to that Agent.
- An explicitly supplied `lead.agent` is never overwritten.
- If the value is empty, new leads remain unassigned.
- If the configured Agent does not exist or is inactive, the lead remains
  unassigned.

The assignment is applied by the Lead `pre_save` signal, so it covers website,
admin, import, and service-created leads consistently.

## Visual workspace shell

The Agent workspace is a role-specific variant of the shared TurkDemy workspace design. It inherits the same outer container, sidebar geometry, content spacing, heading hierarchy, entity navigation styling, responsive behavior, and RTL treatment used by My TurkDemy. Agent organization identity/switching and operational controls remain Agent-specific content.
