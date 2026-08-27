# Agent workspace context

A TurkDemy user may belong to more than one Agent organization. The Agent
workspace therefore always has one **active Agent**.

## Resolution

`apps.agents.services.context.resolve_active_agent()` is the canonical resolver.

- No active Agent memberships: Agent workspace access is denied.
- One membership: that Agent is selected automatically.
- Multiple memberships: the last valid Agent stored in the session is used.
- No stored selection yet with multiple memberships: the user explicitly chooses an Agent.
- Stale or tampered session value: membership is revalidated and the invalid
  value is discarded.

The session key is `active_agent_id`. The session value is never trusted as an
authorization decision.

## Scope

Agent workspace queries are scoped to the active Agent, including:

- dashboard statistics and recent records;
- Applicants;
- Students;
- Applications;
- Messages and unread counts.

A user who belongs to Agent A and Agent B cannot see Agent B records while Agent
A is active. They must explicitly switch to Agent B.

## UI

The top of the Agent workspace sidebar shows the active Agent's logo and company
name. If no logo exists, the first company-name letter is used as a fallback.

When the user has multiple Agent memberships, a **Switch organization** selector
is displayed directly below the Agent identity. Switching changes the active Agent in the session and returns to the Agent Overview. Only organization-neutral Agent list/inbox URLs may be preserved; entity-detail URLs are never carried into the newly selected organization.

The previous generic `AGENT WORKSPACE / Operations` sidebar identity is removed.
