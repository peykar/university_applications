# CHG-0014 — Locale-aware calendar and datetime presentation

Classification: CHANGE
Status: VERIFYING
Date: 2026-09-03

## Request and motivation

Translation-enabled TurkDemy pages localized interface copy but continued to render
human-facing dates/timestamps with Gregorian/English-oriented template formatting.
Persian pages therefore mixed localized RTL UI with Gregorian calendar dates.

## Affected requirements

- `I18N-002` through `I18N-009`
- `BR-I18N-001` through `BR-I18N-006`

## Approved behavior

Canonical Django/Python dates and datetimes remain unchanged. Human-facing rendering
uses one centralized presentation layer selected by active language: English,
Turkish, and Arabic remain Gregorian; Persian uses Solar Hijri/Jalali. Persian uses
Persian month names/digits, Arabic uses Arabic-Indic digits, and timezone-aware
datetimes retain existing local-time semantics.

Machine-readable ISO values and native `datetime-local` control values remain
Gregorian/ISO. No data migration is required.

## Implementation

- Added centralized `localized_date()`, `localized_datetime()` and `localized_time()`
  helpers plus globally available template filters.
- Added deterministic Gregorian-to-Jalali presentation conversion.
- Migrated user-visible date/datetime rendering across customer Requests,
  Applications, messages, Activity, Agent workspace, TODO/communications, document
  review metadata, and public programme deadlines.
- Preserved ISO `<time datetime>` attributes and `datetime-local` input values.
- Added cross-locale, timezone and template-integrity regression tests.
- Encoded Persian/Arabic numeral constants and test expectations with Unicode escapes so Ruff `RUF001` does not mistake intentional localized digits for ambiguous source-code characters.
- Updated localization SDD, documentation, traceability and changelog.

## Verification

- Run `make format`.
- Run `make check`.
- Verify representative EN/FA/TR/AR customer and Agent pages.
