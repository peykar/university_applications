# BUG-0013 — Persisted Unicode catalogue slugs could not be reversed

## Status

Fixed.

## Symptom

Opening a valid Program Detail page could fail while rendering the **Similar programs** section with `NoReverseMatch` when a related legacy/imported program had a persisted non-ASCII slug such as `birûni-üniversite-dentistry-turkish`.

The public, customer apply, and API URL patterns used Django's built-in `<slug:slug>` converter. That converter only accepts ASCII letters, digits, hyphens, and underscores even though historical/imported catalogue rows can already contain Unicode slug characters.

## Fix

Catalogue detail routes now use `<str:slug>` for University and Program lookup paths. This preserves the existing database lookup semantics while allowing Django to reverse and resolve persisted Unicode slug values. The converter remains bounded to a single path segment, so slashes are still rejected.

Updated routes:

- public University Detail
- public Program Detail
- customer Apply Program
- API University Detail
- API Program Detail

No catalogue records or slugs are rewritten, so existing URLs and imported identifiers remain stable.

## Regression coverage

`tests/test_unicode_catalogue_slugs.py` verifies public reverse generation, customer apply reverse generation, and API resolution for representative Unicode University and Program slugs.
