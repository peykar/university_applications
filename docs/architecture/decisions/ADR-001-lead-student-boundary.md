# ADR-001: Lead → Student is a domain transition, not a new person navigation

Status: Accepted

## Context

TurkDemy collects provisional Applicant data in `Lead` and creates a validated
`Student` at finalization.

## Decision

Lead finalization is the domain transition from provisional Applicant to Student.
The transition is atomic from the workflow perspective. The UI continues to
represent the same person/case through Applicant context rather than forcing a
new permanent navigation hierarchy solely because the backing model changed.

Formal Applications belong to Student, not Lead.

## Consequences

- Applicant navigation can expose Applications after conversion.
- Historical Lead interests/activities remain traceable.
- Post-finalization person/document maintenance belongs to Student records.
