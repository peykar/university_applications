# Formal applications

Status: BASELINED
Version: 1.2

## Goal

Define the established TurkDemy behavior for formal applications.

## Requirements

APP-001 — A formal Application MUST belong to a Student and concrete
ProgramOffering.

APP-002 — During Lead finalization, the responsible Agent MAY select zero or more
discussed interests to create as DRAFT Applications. Finalization with zero selected
interests creates no Application. After finalization, Agents MAY still start an
additional Application from discussion history or start one for a new ProgramOffering.

APP-003 — Program-level interests without an Offering MUST require selection of
a concrete active Offering before Application creation.

APP-004 — Creation MUST prevent a second active Application for the same Student
and ProgramOffering.

APP-005 — Creation MUST snapshot Offering tuition and deposit.

APP-006 — Application creation MUST NOT require or persist a direct
LeadProgramInterest → Application relation. Discussion history and formal
Application records remain separate lifecycle concepts.

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
