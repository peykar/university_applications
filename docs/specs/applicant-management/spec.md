# Applicant management

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for applicant management.

## Requirements

APL-001 — An authenticated customer MAY manage multiple Applicants/Leads.

APL-002 — Lead data MUST remain permissive/provisional until finalization.

APL-003 — Authorized Agent users MUST be able to view Applicant data in their
active Agent scope.

APL-004 — Agent users MAY update active Applicant data collected through offline
channels; changes MUST be audited.

APL-005 — Finalized Applicant data MUST NOT be edited through the Lead edit
workflow.

APL-006 — Applicant UI MUST expose focused Profile, Programs, Documents,
Applications and Messages areas with Overview as a summary.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
