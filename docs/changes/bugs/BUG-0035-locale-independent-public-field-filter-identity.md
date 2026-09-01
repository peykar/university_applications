# BUG-0035 — Locale-independent public field-filter identity

Status: DONE
Classification: BUG
Owning capabilities: Catalogue (`CAT-052`) and application-wide localization (`I18N-001`)

## Report

A Persian homepage field link such as `?field=engineering` could open the public
programme catalogue with a localized Persian shell but show `0` results. The field
label could also fall back to English even when another Department row for the same
logical field had a Persian name.

## Cause

The filter itself correctly used the stable canonical `Department.slug_en`, but the
set of public field choices/homepage study fields was built from Department rows
without requiring their University to be active. Legacy/inactive University rows
could therefore publish a canonical field link that had no match in the active
programme-list queryset. Repeated per-University Department rows were also exposed
as separate choices instead of one logical canonical field.

## Implementation

- Keep `field=<slug_en>` as the only public URL/filter identity; do not query
  `slug_fa`, `slug_tr`, or `slug_ar` as alternate identities.
- Restrict public field choices to active Departments with active Programs at active
  Universities.
- Deduplicate field choices by canonical `slug_en` across Universities.
- Prefer a Department row that has an explicit name for the active locale when
  choosing the display representative; retain the canonical English slug as the
  submitted value.
- Group homepage study fields by canonical `slug_en`, count only active-catalogue
  Programs, and exclude inactive-University data.
- Align the homepage active-program count/popular-program source with active
  Universities.

## Regression coverage

`tests/test_program_filters.py` verifies that canonical English field slugs match,
localized slugs are not alternate URL identities, Persian labels can be displayed
while the canonical value stays `engineering`, inactive-University fields are not
published, and the homepage does not create dead field links/count inactive
University Programs.
