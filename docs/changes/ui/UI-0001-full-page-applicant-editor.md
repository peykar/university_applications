# UI-0001 — Full-page Agent applicant editor

Status: DONE
Requested: 2026-08-28

## Request

The Agent Applicant edit form was rendered in a large modal. At realistic field
counts the modal was visually cramped, used browser-looking controls, competed
with the page/footer behind it, and made a long structured edit workflow feel
like a transient action.

Move Applicant editing to a dedicated page and give the form a polished,
responsive workspace presentation.

## Classification

UI / interaction refinement.

The underlying Applicant edit permissions, fields, audit behavior and lifecycle
rules are unchanged. This does not change Applicant domain behavior.

Affected baseline requirements:

- APL-003 — Agent access remains active-Agent scoped.
- APL-004 — Agent edits remain auditable.
- APL-005 — finalized Applicant data remains non-editable through Lead workflow.
- NAV-004 — Applicant Profile remains the owning entity area.

## Resolution

- `/agent/applicants/<lead_id>/edit/` now supports GET and POST.
- GET renders a dedicated Agent workspace edit page.
- Invalid POST renders field errors in place rather than redirecting and losing
  the form context.
- Profile/Overview Edit applicant actions navigate to the dedicated page.
- The Applicant edit modal was removed from Overview/Profile.
- The form is grouped into Personal, Contact & residence, Passport, Education &
  language, Family, and Internal notes cards.
- A sticky desktop summary/action rail and responsive mobile actions were added.
- Existing `AgentLeadEditForm` and shared audit recorder are preserved.

## Verification

- [x] Python syntax validation.
- [x] Static regression assertions updated for full-page editor and field partial.
- [x] No domain/model migration.
- [ ] `make format` — run in project environment.
- [ ] `make check` — run in project environment.
