# BUG-0018 — BaseModel helper ordering still violated DJ012

## Symptom

`make format` still reported DJ012 after BUG-0017.

## Cause

The previous fix moved `Meta`, `save()`, and `clean()`, but left the custom
`_populate_missing_slugs()` helper above `Meta`. Ruff evaluates the complete
Django model declaration order, so `Meta` and `save()` were still considered
to appear after a custom method.

## Fix

Reordered `BaseModel` completely:

1. fields
2. `Meta`
3. `save()`
4. `clean()`
5. `_populate_missing_slugs()`

No slug behavior changed. Normal model saves still populate missing slugs
before persistence, including saves using `update_fields`.
