# Formal applications

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for formal applications.

## Requirements

APP-001 — A formal Application MUST belong to a Student and concrete
ProgramOffering.

APP-002 — Agents MAY start an Application from a discussed interest after Lead
finalization or start one for a new ProgramOffering.

APP-003 — Program-level interests without an Offering MUST require selection of
a concrete active Offering before Application creation.

APP-004 — Creation MUST prevent a second active Application for the same Student
and ProgramOffering.

APP-005 — Creation MUST snapshot Offering tuition and deposit.

APP-006 — When created from a LeadProgramInterest, the interest MAY link to the
created Application and MUST belong to the same Student/Program context.

APP-007 — Application entity navigation MUST provide Overview, Requirements,
Documents, Activity and Messages scoped to that Application.

APP-008 — Applicant → Applications MUST show only that Applicant/Student's
Applications; Agent sidebar Applications MUST show the active Agent's scope.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
