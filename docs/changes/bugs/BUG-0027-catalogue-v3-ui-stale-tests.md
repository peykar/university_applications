# BUG-0027 — Catalogue v3 UI migration left stale regression tests

## Status
Fixed — 2026-08-31

## Symptom
After the Catalogue v3 UI-consumer migration, `make check` passed SDD, Ruff,
formatting, mypy, and Django system checks, but pytest reported three failures.

## Root cause
The failures were stale test expectations/fixtures rather than production
Catalogue v3 behavior:

1. `test_minimum_tuition_includes_matching_currency` assigned an `Intake` to the
   legacy `ProgramOffering.semester` relation and created no canonical
   `OfferingFee` rows.
2. The customer request template assertion still expected the legacy offering
   currency path instead of `display_tuition_fee.currency`.
3. The student application form assertion still expected ordering through
   `semester__name_en` instead of canonical `intake__name_en`.

## Fix
- Build the filter fixture with canonical `intake` relations and structured
  `OfferingFee` tuition rows.
- Assert the customer request UI reads currency from `display_tuition_fee`.
- Assert application offering ordering uses `intake__name_en`.

No production behavior was changed by this bug fix.
