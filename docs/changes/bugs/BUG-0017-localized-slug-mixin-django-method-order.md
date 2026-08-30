# BUG-0017 — LocalizedSlugMixin Django method ordering

## Symptom

`make format` failed with Ruff DJ012 in `apps/core/models.py`.

## Cause

`LocalizedSlugMixin` placed `clean()` before `save()` and its `Meta` class after methods.
Ruff's Django style rule requires the model `Meta` class before methods and `save()` before
custom model methods such as `clean()`.

## Fix

Reordered the existing declarations to:

1. model fields
2. `Meta`
3. `save()`
4. `clean()`
5. custom helper methods

No slug-generation behavior changed. Missing slugs are still generated at model save time,
and `clean()` still generates them before model validation.
