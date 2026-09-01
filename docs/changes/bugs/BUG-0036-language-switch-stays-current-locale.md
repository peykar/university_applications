# BUG-0036 — Language switch can remain on the current locale

Status: FIXED
Requirement: I18N-001
Task: I18N-T13

## Problem

The shared desktop/mobile language selector posted to Django's generic language
view with only `request.path` as its return target. Query state was discarded,
and when Django could not translate a locale-prefixed return URL it could return
the unchanged path. The language cookie could change while the locale prefix in
the URL continued to win in `LocaleMiddleware`, leaving the rendered page in the
old language.

## Fix

- Use a TurkDemy language-switch endpoint that validates the requested locale and
  same-origin return target.
- Prefer Django `translate_url()` for resolvable routes.
- For an unresolved TurkDemy locale-prefixed path, deterministically replace only
  the supported leading locale segment instead of silently retaining the old one.
- Preserve the complete query string from the current page.
- Persist the standard Django language cookie for non-prefixed localized surfaces.
- Cover normal prefixed routes, unresolved prefixed routes, non-prefixed routes,
  query preservation, and unsafe external return targets.
## Follow-up

- Corrected the `translate_url` import to `django.urls.translate_url`, matching Django 5.2 and django-stubs so the localization fix passes mypy.

