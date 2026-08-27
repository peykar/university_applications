# University and program catalogue

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for university and program catalogue.

## Requirements

CAT-001 — A Program MUST belong to one University.

CAT-002 — A Program Department, when present, MUST belong to the same University.

CAT-003 — ProgramOffering MUST hold intake-specific academic year, semester,
tuition and applicable quota/deadline data.

CAT-004 — University recognition/approval flags MUST remain on University and
MUST NOT be duplicated onto Program.

CAT-005 — Listing priority MUST be treated as internal ordering input and MUST
NOT be presented as academic quality/rank/sponsorship.

CAT-006 — Public catalogue filtering MAY use country, city, university, degree,
tuition, language and field/discipline dimensions supported by the data model.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
