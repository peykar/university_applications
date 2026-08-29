# BUG-0009 — django-stubs / mypy compatibility

Status: SUPERSEDED BY BUG-0010
Classification: BUG INVESTIGATION
Date: 2026-08-29

## Initial diagnosis

An earlier `make check` only reported that mypy failed while constructing
`NewSemanalDjangoPlugin`. Without the traceback, this was initially attributed to
a django-stubs / mypy compatibility mismatch and a temporary dependency
restriction was proposed.

## Corrected diagnosis

The later traceback showed that django-stubs was successfully initializing
Django and failed while importing `apps.universities.models`: a parameterized
`models.ManyToManyField[...]` annotation was being evaluated at runtime even
though Django's runtime field class is not subscriptable.

The dependency restriction was therefore not justified by the observed failure
and has been reverted. See `BUG-0010-catalogue-v2-runtime-type-annotation.md`
for the actual fix.
