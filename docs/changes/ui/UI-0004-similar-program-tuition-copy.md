# UI-0004 — Similar-program tuition copy

Status: DONE  
Classification: UI  
Owning capability: Catalogue  
Affected requirement: CAT-043

## Request

Replace the implementation-oriented **“minimum active tuition”** wording on
public Program Detail **Similar programs** cards with customer-facing tuition
copy such as **“Tuition from”**.

## Decision

Keep the existing `min_active_tuition` and `min_active_currency` annotations and
all pricing/filter semantics unchanged. Only the visible card copy changes.
When a minimum active tuition exists, the card shows **“Tuition from”** together
with the formatted amount. The existing unavailable state remains unchanged.

## Implementation

- `templates/public/program_detail.html` now uses the existing translatable
  `Tuition from` string and no longer exposes `minimum active tuition`.
- `docs/program-detail.md` and Catalogue design/tasks/traceability document the
  presentation boundary.
- `tests/test_similar_program_cards_clickable.py` guards the customer-facing copy
  and the existing amount annotation.

## Verification

Run `make format` and `make check`. The SDD validator must continue to report the
same requirement count because this UI refinement does not add domain behavior.
