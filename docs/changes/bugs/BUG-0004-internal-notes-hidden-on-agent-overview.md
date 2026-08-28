# BUG-0004 — Internal notes hidden on Agent Applicant Overview

Status: VERIFYING
Reported: 2026-08-28
Parent change: `CHG-0002-separate-internal-notes-from-applicant-profile`

## Classification

BUG

## Violated requirement

- APL-007 — Internal notes MUST be visible to Agent users on Applicant Overview.

## Expected behavior

The Agent Applicant Overview visibly shows the current private internal note,
including its Private label and dedicated Edit action when editable.

## Actual behavior

The internal-notes panel existed in the template but was nested inside the
legacy `<aside>` element. The Applicant Overview summary CSS intentionally hides
that entire aside:

`.agent-applicant-overview > aside { display: none; }`

As a result, the note was present in source but invisible in the rendered UI.

## Root cause

`CHG-0002` preserved the existing note card without checking its rendered
position against the earlier summary-only Applicant Overview CSS.

## Resolution

Moved the internal-notes panel out of the hidden legacy aside and placed it
directly below the six visible Applicant Overview summary cards. The dedicated
note modal/update endpoint remains unchanged. Added an explicit CSS rule for the
visible Overview note panel.

## Regression coverage

- Internal notes panel must occur before the legacy `<aside>` in the rendered
  template source.
- Applicant Overview CSS must not hide the direct internal-notes panel.
- Existing privacy and dedicated-update regression coverage remains intact.

## Spec impact

Product spec change: No. This restores the behavior already required by APL-007.

## Verification

- Static validation: PASS.
- Full `make check`: pending.
