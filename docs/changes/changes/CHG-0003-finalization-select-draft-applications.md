# CHG-0003 — Select draft applications during Applicant finalization

Status: DISCOVERY
Requested: 2026-08-28

## Request

Change Applicant finalization so the responsible Agent reviews all discussed
programs and chooses which ones should become formal draft Applications as part
of finalization.

Discussed programs include interests added by either the customer or an Agent.

## Motivation

Finalization is the business transition from an Applicant/Lead into a Student.
At that point the Agent should explicitly decide which discussed study choices
are mature enough to become formal Applications instead of requiring a separate
post-finalization conversion step for each interest.

## Classification

CHANGE

This changes existing finalization and Application-creation behavior. It is not
a bug because the current baseline explicitly leaves LeadProgramInterest as
history and creates Applications separately after finalization.

## Affected requirements

- FIN-004 — successful finalization behavior.
- FIN-006 — duplicate/idempotent finalization.
- APP-002 — when a discussed interest becomes an Application.
- APP-003 — a formal Application requires a concrete active ProgramOffering.
- APP-004 — duplicate active Applications must be prevented.
- APP-005 — Offering tuition/deposit must be snapshotted.
- APP-006 — converted LeadProgramInterest links to its Application.

## Current behavior

1. The responsible Agent opens Finalize Applicant.
2. Minimum Student data is reviewed.
3. Finalization creates/reuses Student, copies approved documents, links the
   Lead to Student and marks the Lead FINALIZED.
4. Discussed program interests remain Lead history.
5. An Agent may later create a draft Application from a discussed interest.

## Desired behavior

Finalization becomes a review/selection workflow:

1. Review minimum Student data.
2. Show every unconverted discussed program, regardless of whether its source
   is customer or Agent.
3. The Agent explicitly selects which discussed programs should become draft
   Applications.
4. Every selected program must resolve to exactly one concrete active
   ProgramOffering before confirmation.
5. Final confirmation atomically:
   - creates/reuses the Student;
   - copies approved Lead documents;
   - creates DRAFT Applications for the selected interests;
   - links each selected LeadProgramInterest to its created Application;
   - snapshots Offering tuition/deposit using the existing Application service;
   - finalizes the Lead;
   - records established audit/system communication.
6. Unselected discussed programs remain historical LeadProgramInterest records
   and are not converted.
7. A failure in Student conversion or any selected Application creation rolls
   back the complete finalization operation.

## Proposed acceptance criteria

- FIN-APP-01 — Finalization MUST present all unconverted discussed programs
  from both customer-added and Agent-suggested interests.
- FIN-APP-02 — The responsible Agent MUST explicitly select zero or more
  discussed programs for conversion.
- FIN-APP-03 — Every selected interest MUST resolve to one concrete active
  ProgramOffering before finalization can commit.
- FIN-APP-04 — Each selected interest MUST create a DRAFT Application through
  the canonical Application creation service and link the interest to it.
- FIN-APP-05 — Unselected interests MUST remain unchanged as discussion history.
- FIN-APP-06 — Student creation, document copying, selected Application
  creation and Lead finalization MUST be one atomic transaction.
- FIN-APP-07 — Duplicate/idempotency protections from FIN-006 and APP-004 MUST
  continue to apply.
- FIN-APP-08 — Only the responsible Agent user may make the final selection and
  finalize, preserving FIN-001.
- FIN-APP-09 — Customer-added and Agent-suggested interests MUST be treated
  equally for selection eligibility.

## Open discovery decision

### D-001 — Program interest without a concrete Offering

`LeadProgramInterest.program_offering` is nullable, while APP-001/APP-003 require
a concrete ProgramOffering for every formal Application.

For a selected discussed program that has no Offering yet, finalization needs a
defined UI behavior before this change can be baselined and implemented.

Candidate decision:

A. In the finalization review, show an intake/Offering selector directly under
   every selected program that does not already have an Offering. Finalization
   is blocked until each selected program has a valid active Offering.

B. Do not allow program-level interests without an Offering to be selected
   during finalization; the Agent must first edit the discussed program and
   choose an Offering elsewhere.

Recommended: A. It keeps the finalization workflow complete and matches the
existing APP-003 rule without forcing the Agent to leave the flow.

## Spec changes

- [ ] Resolve D-001.
- [ ] Update `docs/specs/applicant-finalization/spec.md`.
- [ ] Update `docs/specs/applications/spec.md`.
- [ ] Baseline the changed requirements before implementation.

## Design impact

After D-001 is resolved:

- Finalize Applicant changes from a simple confirmation modal into a
  multi-step/review interaction.
- The POST contract must carry selected interest IDs and, where necessary,
  selected Offering IDs.
- `finalize_lead()` must accept an explicit conversion selection or delegate to
  a finalization orchestration service.
- Existing `create_student_application()` remains the canonical Application
  creation primitive.
- The complete operation remains transaction-atomic.
- Applicant/Application activity and finalization messaging should describe the
  Applications created.

## Implementation tasks

Blocked until D-001 and the spec changes are approved.

## Verification

- [ ] Customer- and Agent-added interests are both shown.
- [ ] Selected interests create DRAFT Applications.
- [ ] Unselected interests do not create Applications.
- [ ] Missing/invalid Offering blocks finalization without partial conversion.
- [ ] Duplicate Application protection remains effective.
- [ ] Failure of any selected Application creation rolls back Student/Lead
      finalization.
- [ ] Finalization remains restricted to the responsible Agent.
- [ ] Traceability updated.
- [ ] `make format`
- [ ] `make check`
