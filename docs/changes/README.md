# Change management

Every reported problem or requested behavior is classified before implementation.

## Classification

| Type | Meaning | Product spec first? |
|---|---|---|
| BUG | Implementation violates an approved/baselined requirement | No |
| CHANGE | Desired behavior changes an existing requirement | Yes |
| FEATURE | New capability/behavior | Yes |
| UI | Visual/copy refinement with no domain behavior change | Usually no |
| REFACTOR | Implementation/design change with identical observable behavior | No |
| DISCOVERY | Idea is not defined enough to specify | Discovery first |
| CONFLICT | Code and spec disagree and intended behavior is unclear | Decision first |

## Decision procedure

1. Identify the observable desired behavior.
2. Find the owning capability and requirement IDs.
3. Compare current code, current spec, and desired behavior.
4. Classify the request.
5. Create a change record for non-trivial work.
6. Follow the workflow for that classification.

### BUG

`report -> requirement -> reproduce -> regression test -> fix -> verify -> traceability`

Do not change a correct approved requirement to match defective code.

### CHANGE

`request -> update spec -> approve -> update design -> tasks -> implement -> verify`

### FEATURE

`idea -> discovery if needed -> draft spec -> approve -> design -> tasks -> implement -> verify`

### UI

If scope/permissions/workflow do not change, implement and verify directly.
If information architecture, entity scope, permissions, or workflow changes,
reclassify as CHANGE/FEATURE.

### REFACTOR

Keep behavioral requirements unchanged. Update technical design/tasks where
material, preserve regression coverage, and verify.

### DISCOVERY

Record questions and decisions. Do not implement behavior that depends on an
unresolved decision.

### CONFLICT

Stop. Record code behavior, spec behavior and the unresolved product decision.
Resolve the decision before implementation.

## IDs and locations

Use monotonically increasing IDs within each type:

- `docs/changes/bugs/BUG-0001-<slug>.md`
- `docs/changes/changes/CHG-0001-<slug>.md`
- `docs/changes/features/FEAT-0001-<slug>.md`
- `docs/changes/ui/UI-0001-<slug>.md`
- `docs/changes/refactors/REF-0001-<slug>.md`
- `docs/changes/discovery/DISC-0001-<slug>.md`
- `docs/changes/conflicts/CONFLICT-0001-<slug>.md`

Completed records stay immutable except for factual corrections and are moved to
`docs/changes/archived/<year>/` only when useful. Their IDs are never reused.

## Required fields

A substantial record should capture:

- classification and status;
- report/request and motivation;
- affected requirement IDs;
- expected/current behavior;
- reproduction for bugs;
- decisions/open questions;
- implementation/design impact;
- tests;
- verification result;
- links to spec/design/ADR when applicable.

## Statuses

Suggested statuses:

`REPORTED`, `DISCOVERY`, `SPEC_DRAFT`, `AWAITING_APPROVAL`, `APPROVED`,
`IN_PROGRESS`, `BLOCKED`, `VERIFYING`, `DONE`, `REJECTED`.

A BUG may move directly from `REPORTED` to `IN_PROGRESS` once it is confirmed to
violate an existing requirement.

Current discovery: `DISC-0001-finalization-offering-selection.md` blocks `CHG-0003-finalization-select-draft-applications.md` until resolved.
