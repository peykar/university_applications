# BUG-0002 — Finalized Applicant remained editable by customer

Status: VERIFYING
Reported: 2026-08-28

## Classification

BUG

## Violated requirements

- APL-005 — finalized Applicant data must not be edited through Lead edit.
- BR-FIN-004 — post-finalization person maintenance belongs to Student workflow.

## Expected behavior

A customer cannot open or submit the Lead edit workflow after finalization.

## Actual behavior

`lead_edit()` accepted GET/POST for a finalized Lead.

## Root cause

The customer edit view lacked the lifecycle guard already present in Agent edit.

## Resolution

`lead_edit()` now redirects finalized Leads back to Profile with an explanatory
message. The customer Edit profile action is hidden after finalization.

## Regression tests

- Customer finalized profile edit is blocked.
- Finalized Profile does not expose the edit action.

## Spec/design impact

Product spec change: No.
