# FEAT-0001 — Agent TODOs and Communication Log

Status: VERIFYING
Requested: 2026-08-28

## Classification

FEATURE

## Discovery decisions

The approved V1 decisions are baselined in the TODO Management and
Communication Log specifications. Important decisions include optional generic
subjects, Agent-organization visibility, one optional TODO assignee, CANCELLED
state, reopening, date-only due dates, immutable comments, separate
Communication Log persistence, creator-only communication edits with revision
history, parent aggregation, Activity integration, global workspace pages and
contextual tabs.

## Implementation tasks

- [x] Baseline TODO and Communication Log specifications/design.
- [x] Add generic Agent-owned domain models.
- [x] Add TODO comments, lifecycle/completion metadata and assignee validation.
- [x] Add Communication Log revision history.
- [x] Add global Agent TODO/Communications pages.
- [x] Add Applicant/Application contextual TODO and Communication Log tabs.
- [x] Aggregate Application child subjects on Applicant contextual views.
- [x] Add create-TODO-from-communication workflow.
- [x] Add Agent dashboard TODO/communication summaries.
- [x] Feed Applicant activity for resolvable subjects.
- [x] Add regression coverage and traceability.
- [ ] Generate the fresh migration set with `make makemigrations` in the normal development environment.
- [ ] Run full `make check`.

## Out of scope

TODO reminders, attachments, multi-assignee TODOs, structured University
counterparties, merging Messages with Communication Log, and a new generic
cross-domain Activity persistence model.

## Follow-up bugs

- `BUG-0005-todo-create-form-missing-agent` — active Agent must be bound before ModelForm model validation.
