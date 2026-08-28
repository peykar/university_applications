# DISC-0001 — Offering selection during Applicant finalization

Status: OPEN
Requested: 2026-08-28
Related change: `CHG-0003-finalization-select-draft-applications`

## Question

When an Agent selects a discussed Program during finalization and that
LeadProgramInterest does not yet have a concrete ProgramOffering/intake, where
must the Offering be selected?

## Why this blocks implementation

A formal Application cannot exist for Program alone. APP-001 and APP-003 require
a concrete ProgramOffering, while LeadProgramInterest intentionally allows
`program_offering = NULL`.

## Options

### A — Select Offering inside finalization

The selected program expands to an Offering/intake selector. Finalization cannot
be confirmed until every selected program resolves to a valid active Offering.

### B — Require Offering before finalization

A program-level interest without an Offering is disabled in finalization and the
Agent must leave the workflow and choose an Offering elsewhere first.

## Recommendation

Option A.

It keeps the business decision in one finalization workflow and reuses the same
active-Offering validation already required by Application creation.

## Decision

OPEN — awaiting product-owner answer.
