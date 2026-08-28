# FEAT-0002 — Create draft applications during applicant finalization

Status: IMPLEMENTED

## Decision

When a Lead is finalized, the responsible Agent may select zero or more programs
that were already discussed with the customer. Eligible programs are customer-added
`LeadProgramInterest` records and Agent-suggested interests. Selecting none still
finalizes the Lead into a Student and creates no Application. Each selected program
must resolve to a concrete active `ProgramOffering`; Program-level interests require
the Agent to choose the offering.

Successful finalization creates/reuses the Student and creates one DRAFT Application
for each selection in the same atomic operation. Unselected interests remain
exploratory history and may be converted later.

## Affected requirements

- `FIN-007`–`FIN-009`
- `APP-002`, `APP-003`, `APP-006`
- `BR-FIN-005`, `BR-APP-002`

## Verification

Covered by the Lead finalization, Agent finalization UI and atomic finalization tests.
