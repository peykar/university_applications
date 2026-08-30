# BUG-0019 — django-stubs does not expose SlugField.allow_unicode

## Symptom

`make check` failed in mypy with:

`"SlugField[Any, Any]" has no attribute "allow_unicode" [attr-defined]`

## Cause

Django's runtime `SlugField` exposes the `allow_unicode` attribute, but the installed
django-stubs type definition does not currently declare that attribute.

## Fix

Read the runtime attribute with `getattr(field, "allow_unicode", False)` and coerce it
to `bool` before passing it to `django.utils.text.slugify`.

This preserves the intended model-level behavior:
- English slug fields use ASCII slugification.
- Persian, Turkish, and Arabic localized slug fields use Unicode slugification.
- Missing/unknown attributes safely fall back to Django's ASCII behavior.

No slug-generation semantics changed.
