# BUG-0007 — Messages workspace regression tests stale after redesign

Status: FIXED
Reported: 2026-08-29

## Report

`make check` reported two failures after the customer Request Messages redesign even though the rendered UI and messaging form matched the new SDD.

## Classification

BUG

## Violated requirements

- `CRQ-083` — the regression test must inspect the actual messaging form that owns the attachment input.
- `CRQ-086` — the unassigned-advisor test must assert the current customer-safe unavailable-state copy.

## Expected behavior

The regression suite verifies the v1.26 Messages contract and passes when the implementation satisfies it.

## Actual behavior

One test still asserted the pre-redesign unavailable-state sentence. Another searched `apps/leads/forms.py` for the attachment widget even though `MessageForm` is defined in `apps/messaging/forms.py`.

## Reproduction

1. Run `make check` against the v1.26 Messages workspace delivery.
2. Observe the two stale-test failures.

## Root cause

The Messages implementation changed correctly, but two regression-test assertions were not aligned with the new copy and the existing messaging-form ownership boundary.

## Resolution

Updated the unassigned Request assertion to the v1.26 customer-safe sentence and made the workspace structural test inspect `apps/messaging/forms.py` for `chat-attachment-input`.

## Regression tests

- [x] Test asserts the current unassigned-advisor state.
- [x] Composer test inspects the actual `MessageForm` source.
- [x] Existing no-composer negative assertion remains covered.

## Spec/design impact

Product spec change: No.

Design update: None. This is test alignment with the already-approved v1.26 design.

## Verification

- [ ] `make format`
- [ ] `make check`
- [x] SDD checker
- [x] Python compilation
- [x] Targeted static regression assertions

Result: repository-only checks pass. Full pytest could not run in this sandbox because Django is not installed; rerun `make check` in the project environment.
