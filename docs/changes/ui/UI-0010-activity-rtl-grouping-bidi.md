# UI-0010 — Cohesive RTL Activity timeline

Status: IMPLEMENTED
Requested: 2026-09-03

## Request

Improve the Agent Applicant Activity timeline seen in the Persian workspace: keep
actor/date metadata visually associated with its event and make mixed-direction
dynamic values more robust without changing Activity semantics or ordering.

## Classification check

UI only. No Activity data, event type, ordering, localization semantics,
permissions, audit history, or business workflow changes.

## Decision

- Each event heading and its actor/timestamp form one compact metadata stack instead
  of using full-width `space-between` distribution.
- Logical `start` alignment is used so Persian/Arabic anchor naturally on the right
  and English/Turkish on the left.
- Actor names, localized/free-form descriptions, recommendation notes, and structured
  old/new values are bidi-aware. Human/domain text remains verbatim.
- The existing timeline rail/dot side, event ordering, filters and pagination remain
  unchanged.
- On mobile, actor/timestamp metadata may wrap rather than collide.

## Implementation

- Added dedicated `activity-byline`, `activity-actor`, `activity-description`, and
  metadata separator hooks to the Activity template.
- Reworked `.activity-meta` from edge-distributed flex layout to a compact,
  start-aligned grid.
- Applied `dir="auto"` and `unicode-bidi: plaintext` to mixed-direction content
  boundaries and old/new audit values.
- Added structural regression coverage in `tests/test_agent_activity_page.py`.
- Corrected the structural regression to inspect the `.activity-meta` CSS rule itself rather than banning a generic `space-between` declaration elsewhere in the shared stylesheet.
- Added `AUD-010` and synchronized Activity SDD traceability.

## Acceptance

- [x] Actor/date metadata stays near the event it describes on wide screens.
- [x] LTR and RTL layouts use logical alignment rather than hard-coded physical sides.
- [x] Mixed Persian/Arabic + English values remain readable.
- [x] Profile-change old/new values determine their own text direction.
- [x] Event order, timeline rail, filters and business behavior are unchanged.
