# FEAT-0011 — Semantic structured-fee order

## Change

Django Admin structured-fee summaries now use a stable business-readable order
instead of sorting alphabetically by `fee_type`.

The order is:

1. Tuition / list fee
2. Discounted tuition
3. Advance payment
4. Cash payment
5. Installment total
6. Deposit
7. Preparatory / foundation tuition
8. Application fee
9. Registration fee
10. Other

This ensures common university fee records scan naturally, including the
requested Tuition → Advance payment → Preparatory/Foundation sequence.

## Scope

Presentation only. No model, migration, importer, API, or persisted fee data is
changed.
