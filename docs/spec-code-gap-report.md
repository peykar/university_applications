# Spec ↔ code baseline gap report

Date: 2026-08-28
Status: Initial SDD baseline

This report compares the intended architecture documented in the repository with
the implementation inspected while creating the SDD baseline. It deliberately
does not invent missing product decisions.

## Summary

| Area | Classification | Finding |
|---|---|---|
| Active Agent context | MATCH | Central active-Agent resolver and scoped workspace behavior exist. |
| Lead lifecycle/finalization | MATCH | Established lifecycle and conversion services/docs align with baseline. |
| Generic messaging | MATCH | Generic Conversation/Message/participant-state models exist. |
| Program interest vs Application | MATCH | Separate models/workflows exist. |
| Applicant entity navigation | MATCH | Focused Applicant tabs exist. |
| Application entity navigation | MATCH | Focused Application tabs exist. |
| Program recommendations | MATCH | REF-0002 moved Agent recommendation orchestration into a dedicated transactional domain service. |
| Application requirements | SPEC GAP | Current project explicitly says requirements are not yet a full separate workflow/model. Do not infer requirements from document attachment. |
| Program recommendation atomicity | RESOLVED | REF-0002 wraps recommendation creation, activity and system message in one explicit transaction boundary. |
| Traceability | PROCESS GAP | Existing tests predate requirement IDs; exact requirement→test mapping is not yet complete. |
| Legacy docs | DOC DEBT | Existing flat `docs/*.md` remain useful but overlap with new canonical product/architecture/spec docs. |

## G-001 — Program recommendation service boundary — RESOLVED

Classification: RESOLVED CODE GAP / design debt  
Resolved by: `REF-0002`

`apps.leads.services.recommendations.recommend_program(...)` now owns duplicate
and user-interest behavior, Agent recommendation updates, attribution, and the
creation of the recommendation/activity/system-message side effects. New
recommendation creation is protected by an explicit `transaction.atomic`
boundary. The Agent view retains HTTP scoping, request parsing, flash messages
and redirects. No intentional user-visible behavior changed.

## G-002 — Application requirements domain

Classification: SPEC GAP  
Priority: Resolve before implementing real university requirement management.

Existing documentation states that attaching `ApplicationDocument` does not
define whether a document type is required. The current `is_required` field/data
is insufficient to silently invent a complete requirements workflow.

Before implementation, write a new/expanded `APP`/`DOC` spec answering:

- Are requirements defined by University, Program, Offering or Application?
- Are requirements document-only, or can they be non-document requirements?
- Can an Agent override requirements for one Application?
- What statuses exist (missing, supplied, accepted, waived, not applicable)?
- How is a requirement satisfied by a StudentDocument?
- Who can mark it satisfied/waived?
- What does the customer see?

## G-003 — Requirement-level traceability

Classification: PROCESS GAP  
Priority: Incremental.

Existing tests are substantial but were written before stable requirement IDs.
Do not fabricate exact mappings. Whenever a capability is touched, update its
`traceability.md` with exact implementation files and named tests.

## G-004 — Documentation authority

Classification: DOC DEBT  
Priority: Medium.

The repository already contains useful historical flat docs. New authority is:

1. `docs/product/*` for canonical vocabulary/global business rules.
2. `docs/architecture/*` and ADRs for architecture.
3. `docs/specs/*/spec.md` for capability behavior.
4. capability `design.md` for implementation mapping.
5. old flat docs for operational/history/detail until migrated.

If an old doc conflicts with an approved spec, the approved spec wins. Update or
retire the conflicting old doc in the same change.

## G-005 — Automated spec linting

Classification: PROCESS OPPORTUNITY  
Priority: Low.

A future tooling task may validate requirement ID uniqueness, missing
traceability rows and DRAFT/OPEN specs. This baseline does not add a new runtime
dependency or CI tool merely for documentation validation.

## Recommended next SDD change

G-001 was completed by `REF-0002`. The next product change should follow the
normal change-driven SDD workflow. G-002 remains a discovery/specification gap
and must be resolved before implementing a full Application Requirements domain.


## 2026-08-28 alignment follow-up

The following baseline issues were resolved after the initial report:

- Customer Lead profile editing is now blocked after finalization (`APL-005`,
  `BR-FIN-004`).
- Customer Lead document upload/replacement is now blocked after finalization
  (`DOC-001`, `STU-003`, `BR-FIN-004`), with mutation controls hidden in the UI.
- `FIN-005` was clarified to match the already-established atomic one-step
  finalization design: validation metadata is persisted and one `FINALIZED`
  activity is emitted. There is intentionally no intermediate `VALIDATED`
  activity/message.
- The Applicant edit i18n template crash is recorded as a separate fixed BUG.
