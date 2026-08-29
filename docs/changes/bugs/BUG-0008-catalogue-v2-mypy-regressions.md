# BUG-0008 — Catalogue v2 mypy regressions

## Problem

Catalogue v2 passed Ruff but introduced six mypy errors in the university models/admin: an untyped explicit-through many-to-many field, an inferred integer reused for a Decimal duration, nullable relation dereferences, and an optional POST value used directly as a UUID primary-key lookup.

## Resolution

- Annotated `Program.instruction_languages` for django-stubs.
- Kept fractional-year Decimal calculation in a separately named variable.
- Guarded nullable legacy language and catalogue source relations before dereference.
- Normalized the posted Program primary-key value to `str` before the admin queryset lookup.

No domain behavior or SDD requirement changed.

## Verification

- Python compilation passes in the delivery environment.
- SDD validation passes: 19 capabilities / 254 requirements.
- Full mypy/`make check` requires the project dependency environment and should be rerun locally.
