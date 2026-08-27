# Applicant finalization

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for applicant finalization.

## Requirements

FIN-001 — Only the responsible Agent user MAY finalize an active assigned Lead.

FIN-002 — Finalization MUST validate the minimum Student data before committing
conversion.

FIN-003 — Validation failure MUST NOT create a partial Student conversion and
MUST leave the Lead active with correction errors.

FIN-004 — Successful finalization MUST create/reuse Student, copy approved Lead
documents, link Lead to Student, record conversion time, and set Lead finalized.

FIN-005 — Successful finalization MUST record validation/finalization audit
events and established system communication.

FIN-006 — Finalization MUST be safe against duplicate conversion of the same Lead.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
