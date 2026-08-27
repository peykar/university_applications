# BUG-0003 — Finalized Lead documents remained mutable by customer

Status: VERIFYING
Reported: 2026-08-28

## Classification

BUG

## Violated requirements

- DOC-001 — Applicant document upload is pre-finalization behavior.
- STU-003 — post-finalization reusable document maintenance belongs to Student.
- BR-FIN-004 — post-finalization document maintenance leaves historical Lead.

## Expected behavior

After finalization, the customer can view historical Lead documents but cannot
upload a new LeadDocument or replace an existing LeadDocument.

## Actual behavior

Customer upload and replacement POST endpoints remained available and the UI
continued to render mutation controls.

## Root cause

The Lead document customer endpoints had no finalized-state guard.

## Resolution

Upload/replacement endpoints now reject finalized Lead mutations and redirect to
the Applicant Documents page. Upload and replacement controls are hidden after
finalization and a read-only explanation is displayed.

## Regression tests

- Finalized customer Lead upload is blocked.
- Finalized customer Lead replacement is blocked.
- Finalized document UI does not expose mutation controls.

## Spec/design impact

Product spec change: No.
