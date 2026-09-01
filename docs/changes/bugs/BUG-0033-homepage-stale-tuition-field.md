# BUG-0033 — Homepage queries removed ProgramOffering tuition field

Status: DONE
Classification: BUG
Owning capability: Catalogue (`CAT-043`)

## Report

Loading the public homepage could raise `FieldError: Unsupported lookup 'tuition'
for UUIDField or join on the field not permitted`.

## Cause

The homepage Popular Programs query still annotated `offerings__tuition`, a
Catalogue v2 field removed by the v3 structured-fee cutover. Catalogue v3 stores
tuition in active `OfferingFee` rows.

## Implementation

The homepage now uses the existing canonical `annotate_min_active_tuition()`
helper. The template reads `min_active_tuition` and `min_active_currency`, so the
amount and currency come from the same structured fee row rather than an
unrelated first offering.

## Regression coverage

Catalogue v3 UI contract coverage asserts that the homepage uses the canonical
structured-fee annotation and contains no `offerings__tuition` lookup.
