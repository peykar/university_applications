# Applicant finalization

Status: BASELINED
Version: 1.3

## Goal

Define the established TurkDemy behavior for applicant finalization.

## Requirements

FIN-001 — Only the responsible Agent user MAY finalize an active assigned Lead.

FIN-002 — The Agent MUST review Student data on a dedicated full-page Create
Student Record form. The form MUST be prefilled from the Lead, remain editable,
and validate the resulting Student data before conversion commits.

FIN-003 — Validation failure MUST NOT create a partial Student conversion and
MUST leave the Lead active with correction errors.

FIN-004 — Successful finalization MUST create/reuse Student, transfer only the
Lead documents selected by the Agent, link Lead to Student, record conversion
time, and set Lead finalized.

FIN-005 — Successful finalization MUST record the finalization audit event,
persist validation metadata (`validated_by`/`validated_at`), and send the
established system communication. A separate intermediate VALIDATED activity is
not required.

FIN-006 — Finalization MUST be safe against duplicate conversion of the same Lead.

FIN-007 — During finalization, the responsible Agent MAY select zero or more
discussed LeadProgramInterest records. Eligible interests are those added by the
customer or suggested by an Agent. Selecting no discussed program MUST NOT block
Student finalization.

FIN-008 — Every selected discussed Program MUST have an active ProgramOffering
selected on the conversion form. When the interest already has an active offering,
that offering SHOULD be preselected but the Agent MAY change it.

FIN-009 — Successful finalization MUST create one DRAFT Application for each
selected discussed ProgramOffering. The source LeadProgramInterest MUST NOT be
persistently linked to the resulting Application.

FIN-010 — The Applicant page MUST expose the action label `Create Student Record`
and open a dedicated conversion page rather than a modal.

FIN-011 — The conversion page MUST list all Lead documents. Verified documents
MUST be selected by default and unverified documents MUST be unselected by default.

FIN-012 — The Agent MAY independently select or deselect any Lead document.
Deselecting a verified document MUST NOT revoke its existing verification status.

FIN-013 — Selecting an unverified Lead document MUST approve/verify that Lead
document as part of the successful conversion and then transfer it to the Student
document library.

FIN-014 — Only selected Lead documents MUST be copied/reused as StudentDocument
records; unchecked documents MUST remain only in Lead document history.

FIN-015 — The conversion form MUST preserve submitted Student fields, document
choices, program choices and offering choices when validation fails where practical.

FIN-016 — Student creation, selected document approval/transfer, zero-or-more
DRAFT Application creation, Lead transition, audit and communication MUST execute
within the same database transaction. Any validation or persistence failure MUST
leave the Lead unfinalized and MUST NOT commit partial database conversion state.

FIN-017 — Existing LeadDocument → StudentDocument conversion provenance MAY be
retained to prevent duplicate document conversion. No equivalent persistent
LeadProgramInterest → Application provenance relation is required.

FIN-018 — The responsible Agent MAY complete a `reopened` converted Lead through the finalization action. This MUST reuse the existing Student and MUST NOT repeat Student creation or Lead-document transfer.

FIN-019 — Re-finalizing a reopened Lead MUST preserve existing active Applications and the original `converted_at` provenance, create DRAFT Applications only for selected offerings that do not already have an active Application for that Student, record finalization activity/communication, and return the Lead to `finalized`.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
