# BUG-0010 — Catalogue v2 runtime type annotation breaks django-stubs startup

## Status
Fixed.

## Problem
`Program.instruction_languages` used a parameterized Django model field annotation directly at runtime:

```python
instruction_languages: models.ManyToManyField[ProgramLanguage, ProgramLanguage] = ...
```

On the installed Django runtime, `ManyToManyField` is not subscriptable. The django-stubs mypy plugin initializes Django before checking application types, so importing `apps.universities.models` raised `TypeError` and mypy never reached normal static analysis.

## Resolution
The annotation is now a string literal:

```python
instruction_languages: "models.ManyToManyField[ProgramLanguage, ProgramLanguage]" = ...
```

This preserves the generic information for mypy/django-stubs without evaluating the subscription while Django imports the model module.

The previous temporary dependency restriction from BUG-0009 was also removed. The traceback showed that the immediate failure was application import-time annotation evaluation rather than a demonstrated mypy/django-stubs version incompatibility. Dependency ranges are restored to the project's prior policy.

## Verification
Run:

```bash
make check
```

The regression is specifically verified when `uv run mypy apps turkdemy` can initialize Django and proceed past model import.
