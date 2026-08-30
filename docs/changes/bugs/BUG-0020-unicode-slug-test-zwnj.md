# BUG-0020 — Unicode slug regression fixture contained a ZWNJ

## Symptom

The full test suite failed in
`test_import_accepts_native_unicode_localized_slugs` because `slug_fa` failed
Django's Unicode slug validation.

## Cause

The Persian test slug `مهندسی-نرم‌افزار` contained U+200C ZERO WIDTH NON-JOINER
between `نرم` and `افزار`. ZWNJ is legitimate Persian typography in normal text,
but Django's Unicode slug validator accepts Unicode letters/numbers plus
underscores and hyphens; ZWNJ is not a valid slug character.

The localized name remains `مهندسی نرم‌افزار`, including correct Persian
typography. Only the URL slug fixture is normalized to `مهندسی-نرمافزار`.

## Fix

Use a genuinely valid native-Unicode Persian slug in the importer regression
test. Do not weaken Django slug validation and do not silently normalize
explicitly supplied invalid slugs during import.

Model-generated slugs already use Django `slugify(..., allow_unicode=True)`,
which removes unsupported formatting characters when generating a missing slug.
