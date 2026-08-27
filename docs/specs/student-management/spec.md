# Student management

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for student management.

## Requirements

STU-001 — Student represents validated/finalized admissions data.

STU-002 — A Student created from a Lead MUST retain traceability to its source Lead.

STU-003 — Post-finalization reusable document maintenance MUST occur on Student,
not historical Lead.

STU-004 — Student MUST retain its Agent relationship for downstream Application
workflows.

STU-005 — Applicant-facing navigation MAY continue representing the same person
without introducing a separate permanent Student entity navigation layer.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
