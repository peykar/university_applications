# CHG-0001 — Clarify finalization audit semantics

Status: DONE
Requested: 2026-08-28

## Classification

CHANGE — specification correction to the SDD baseline, not a product behavior
change.

## Affected requirement

- FIN-005

## Context

The initial SDD baseline said successful finalization records
"validation/finalization audit events", which implied two activities. The
pre-existing architecture and regression tests intentionally model finalization
as one atomic business operation with no intermediate validated phase.

## Decision

FIN-005 now requires:

- persisted validation metadata (`validated_by`, `validated_at`);
- one `FINALIZED` LeadActivity;
- the established finalization system message.

A separate `VALIDATED` activity/message is not required.

## Implementation impact

None. Existing one-step `finalize_lead()` behavior remains authoritative and
already matches the clarified requirement.
