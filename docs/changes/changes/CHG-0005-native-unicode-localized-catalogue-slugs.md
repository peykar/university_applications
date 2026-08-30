# CHG-0005 — Native Unicode localized catalogue slugs

Status: DONE
Classification: CHANGE
Capability: Catalogue
Requirements: CAT-033

## Request and motivation

Localized catalogue slugs were stored with Persian, Turkish, and Arabic text by
Rasa/imported data, but the shared Django `SlugField` configuration used
ASCII-only validation. Admin edits and normalized programme imports therefore
rejected valid values such as `مدیپول-استانبول`, `tıp`, and `الطب`, even though
catalogue routes had already been changed to resolve persisted Unicode slugs.

## Approved behavior

- `slug_en` remains ASCII-only and remains the deterministic normalized-import
  key.
- `slug_fa`, `slug_tr`, and `slug_ar` accept Django-valid Unicode slugs.
- The policy is applied through the shared localized-slug contract, so catalogue
  models and their geography dependencies validate consistently.
- Existing slug values are not rewritten or transliterated.
- Public/application/API routes continue accepting a Unicode slug as one path
  segment.

## Implementation

`apps/core/mixins.py` sets `allow_unicode=True` on the Persian, Turkish, and
Arabic `SlugField`s only. The normalized JSON importer needs no special bypass:
its existing `full_clean()` now enforces the approved model policy.

Because Django records `allow_unicode` in model state, deployments should run
`makemigrations` and `migrate` using the project's normal migration workflow.
This change alters validation semantics rather than the database column type or
stored values.

## Verification

Regression tests cover native-script University and Program slugs, assert the
shared field configuration on catalogue/geography entities, retain ASCII-only
English slug validation, and preserve the existing Unicode route coverage.
