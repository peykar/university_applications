# CHG-0011 — Recommendation reason visible in overview and activity

Status: IMPLEMENTED
Requested: 2026-09-03

## Request

When an Agent recommends a Program with a customer-understandable reason, show
that reason on the customer Request Overview program card and make it visibly
part of the PROGRAM_SUGGESTED activity presentation. The Agent activity timeline
should expose the same reason for the event.

## Motivation

The recommendation service already persists the reason on the
`LeadProgramInterest` and copies it to structured activity metadata. Before this
change, the customer Programs tab and system message exposed the reason, while
the Request Overview program card and activity timelines omitted it.

## Classification

CHANGE

## Affected requirements

- `PRG-003` — recommendation may include a customer-understandable reason.
- `PRG-006` — recommendation creates a customer-visible PROGRAM_SUGGESTED activity.
- `PRG-010` — reason presentation on Overview and recommendation activity.

## Desired behavior

- Customer Request Overview program cards show an Agent recommendation reason
  directly beneath the advisor-suggestion source when one exists.
- Customer Progress shows the reason beneath the PROGRAM_SUGGESTED event label.
- Agent Applicant Activity shows the same structured reason beneath the Program
  suggested event.
- No reason placeholder is shown when the reason is blank.
- Internal notes are never used as or exposed as a recommendation reason.

## Design impact

No schema or service mutation change. Presentation consumes existing
`LeadProgramInterest.suggestion_reason` and
`LeadActivity.metadata["suggestion_reason"]`. The activity description remains a
separate stable event description.

## Verification

- [x] Customer Overview program-card structural regression coverage.
- [x] Customer Progress structured-reason regression coverage.
- [x] Agent activity structured-reason regression coverage.
- [x] Traceability updated.
- [ ] `make format`
- [ ] `make check`
