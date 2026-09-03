# CHG-0013 — Localized structured Activity rendering

Classification: CHANGE
Status: VERIFYING
Date: 2026-09-03

## Request and motivation

Agent Activity type labels were translated, but predefined event descriptions were
rendered from persisted English text. This made the same audit timeline partially
English when the interface language was Persian, Turkish, or Arabic.

## Affected requirements

- `BR-AUD-004`
- `AUD-008`
- `AUD-009`

## Approved behavior

Predefined Activity events render in the viewer's active locale at read time.
Semantic event data remains structured; dynamic names/IDs/reasons are interpolated
without treating user/domain values as translatable prose. Historical recognized
English event descriptions continue to localize without rewriting audit rows.
Unknown/free-form descriptions remain unchanged.

## Implementation

- Added the centralized `localized_activity_description()` presentation service.
- Added `LeadActivity.localized_description`.
- Updated the Agent Activity timeline to render localized descriptions and structured change-field labels.
- Enriched predefined Activity producers with semantic metadata for programs,
  assignments, documents, close/reopen actions, and finalization.
- Added legacy pattern support for existing Activity rows.
- Added and compiled FA/TR/AR gettext entries for predefined sentences.

## Verification

- Added `tests/test_activity_localization.py`.
- Existing localization-integrity coverage validates compiled catalogs.
- SDD/format/full test verification remains pending `make format` and `make check`
  in the complete project environment.
