# Entity-level navigation

## Hierarchy

TurkDemy navigation has three persistent conceptual levels:

1. Global: public discovery and account/workspace entry.
2. Workspace: My TurkDemy or Agent workspace.
3. Entity: Customer Request, Agent Applicant, or Application.

A fourth permanent navigation bar should normally be avoided. Deeper resources
use breadcrumbs/back links and local actions.

## Customer Request / Agent Applicant entity

Customer Request:

`Overview | Profile | Programs | Documents | Messages`

Agent Applicant:

`Overview | Profile | Programs | Documents | Applications | Todos | Communication Log | Messages`

The customer presentation deliberately hides Lead/Student/Application lifecycle
terminology. The Agent view keeps operational domain language.

## Application entity

Customer and Agent:

`Overview | Requirements | Documents | Activity | Messages`

Requirements currently correspond to required ApplicationDocument records.
Activity is currently composed from timestamps, documents and application
messages; this is intentionally documented as an interim implementation.

## Scope examples

- Agent sidebar / Applications: every application available to the Agent.
- Agent Applicant / Applications: applications for the selected applicant only.
- Application / Documents: documents attached to one application only.
- My TurkDemy / Messages: customer inbox across contexts.
- Request / Messages: selected customer request conversation.
- Application / Messages: selected application conversation.

## URL design

Customer Request (internal route names currently remain Lead-based):

- `/applicants/<id>/`
- `/applicants/<id>/profile/`
- `/applicants/<id>/programs/`
- `/applicants/<id>/documents/`
- `/applicants/<id>/applications/`
- `/applicants/<id>/messages/`

Customer Application:

- `/applications/<id>/`
- `/applications/<id>/requirements/`
- `/applications/<id>/documents/`
- `/applications/<id>/activity/`
- `/applications/<id>/messages/`

Agent equivalents live below `/agent/`.

POST message endpoints use `/messages/send/` so GET navigation URLs remain
readable and bookmarkable.
