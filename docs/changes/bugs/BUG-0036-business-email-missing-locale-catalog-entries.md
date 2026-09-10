# BUG-0036 — Business email locale catalog entries missing

Status: DONE
Classification: BUG
Owning capability: Mail (`MAIL-006`–`MAIL-016`)

## Report

After FEAT-0013, `make check` failed the application localization-integrity test because the new
business-email gettext literals were not present in the compiled Persian, Turkish, and Arabic
catalogs.

## Cause

The FEAT-0013 implementation marked business-email subjects/body strings for translation, but the
corresponding locale catalog entries were not added and compiled before delivery.

## Implementation

- Added translations for all 31 FEAT-0013 business-email and preview strings in Persian (`fa`),
  Turkish (`tr`), and Arabic (`ar`).
- Preserved all named interpolation placeholders such as `%(name)s`, `%(url)s`, and `%(status)s`.
- Recompiled each `django.po` catalog to `django.mo`.

## Regression verification

A catalog-level replication of
`TranslationEnabledSurfaceTests.test_literal_interface_translations_exist_for_all_supported_non_english_locales`
reports zero missing interface gettext literals for `fa`, `tr`, and `ar`.
