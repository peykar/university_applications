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
| Program recommendations | PARTIAL DESIGN DEBT | Agent recommendation behavior exists, but orchestration currently lives in Agent views rather than a dedicated domain service/transaction. |
| Application requirements | SPEC GAP | Current project explicitly says requirements are not yet a full separate workflow/model. Do not infer requirements from document attachment. |
| Program recommendation atomicity | CODE GAP | Recommendation creates interest, activity and system message as separate operations; design should define an atomic service before expanding this workflow. |
| Traceability | PROCESS GAP | Existing tests predate requirement IDs; exact requirement→test mapping is not yet complete. |
| Legacy docs | DOC DEBT | Existing flat `docs/*.md` remain useful but overlap with new canonical product/architecture/spec docs. |

## G-001 — Program recommendation service boundary

Classification: CODE GAP / design debt  
Priority: High before further recommendation features.

Current Agent recommendation behavior creates/updates `LeadProgramInterest`,
creates `LeadActivity`, and sends a system message from Agent view code.

Target design:

```text
recommend_program(
    *,
    lead,
    program,
    agent_user,
    reason="",
) -> LeadProgramInterest
```

The service should own duplicate/user-interest behavior, audit side effects and
system-message side effects under an explicit transaction boundary.

Do not change user-visible behavior merely as part of this refactor.

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

Before adding another large feature, perform G-001 as a behavior-preserving
refactor using `PRG-002` through `PRG-007` as acceptance requirements. Then use
the resulting service pattern for subsequent cross-model workflows.
