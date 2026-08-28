# CHG-0002 — Separate internal notes from Applicant profile editing

Status: VERIFYING
Requested: 2026-08-28

## Classification

CHANGE

## Problem

`Lead.notes` was included in `AgentLeadEditForm`, mixing private Agent
case-management context with Applicant/person profile data. The note had a
dedicated update workflow and an Agent-only Overview card, but its ownership was
not explicit in the baseline requirement.

## Spec change

Adds `APL-007`.

Internal notes are now defined as private Agent case-management data:

- excluded from Applicant profile editing;
- visible prominently on Agent Applicant Overview;
- edited only through the dedicated internal-note workflow;
- audited as `INTERNAL_NOTES_UPDATED`;
- never customer-visible;
- historical/read-only on the finalized Lead.

## Design

No schema change. `Lead.notes` remains the storage field for the current private
case summary. A separate note-history model is out of scope; structured
LeadActivity remains the audit history.

## Tasks

- [x] Add APL-007 to Applicant Management spec.
- [x] Document internal-note ownership in design.
- [x] Remove `notes` from `AgentLeadEditForm`.
- [x] Remove Internal Notes section from full-page Applicant editor.
- [x] Keep/promote Internal Notes card on Agent Applicant Overview.
- [x] Keep dedicated private audited note update workflow.
- [x] Add/update regression coverage.
- [x] Update traceability.
- [ ] Run full `make check`.

## Acceptance

1. Agent Applicant edit form cannot modify `Lead.notes`.
2. Agent Applicant Overview visibly renders current internal notes and a Private
   label.
3. Active notes are editable only through the dedicated internal-note endpoint.
4. Note activity remains Agent-only.
5. Customer Applicant UI does not expose `Lead.notes`.

## Follow-up

- `BUG-0004-internal-notes-hidden-on-agent-overview` fixes the rendered visibility regression discovered after this change.
