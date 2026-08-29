# FEAT-0005 — Customer Request Messages workspace

Status: DONE
Classification: FEATURE
Date: 2026-08-29

## Request

Bring the customer Request **Messages** tab into the same simplified workspace design as
Profile, Programs, and Documents, with a professional conversation presentation on both
desktop and mobile.

## Decisions

- Use one page title: **Messages**.
- Customer messages are labeled **You** and align to logical end.
- Agent messages use full name when available, otherwise **Your advisor**, and align to logical start.
- System messages are **TurkDemy** events with a centered neutral treatment.
- Both desktop and mobile retain complete date + time message timestamps.
- Desktop retains Request context; mobile hides it for a focused conversation workspace.
- Composer uses one textarea, **Attach file** affordance, selected-file feedback, and **Send**.
- No separate start-conversation action is introduced.
- Agent-less Requests remain message-unavailable until assignment.

## Requirements

CRQ-080 through CRQ-086.

## Implementation

- `templates/leads/lead_section.html`
- `apps/messaging/forms.py`
- `static/css/turkdemy.css`
- customer-request SDD/design/tasks/traceability
- customer messaging documentation and regression tests

## Verification

- SDD validation
- Python compilation
- targeted customer Request structural tests where dependencies permit
- full `make check` to be run in the project environment
