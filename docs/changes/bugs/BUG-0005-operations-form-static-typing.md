# BUG-0005 — Operations forms fail static checks

Status: VERIFYING
Reported: 2026-08-28

## Report

`make format`/`make check` failed in `apps/operations/forms.py`: Ruff rejected mutable
`Meta.widgets` class attributes and mypy could not prove that `assignee` is a
`ModelChoiceField` or that its queryset is non-null.

## Classification

BUG

## Violated requirements

- `TODO-003` — TODO assignee is an optional Agent user and must be constrained to the owning Agent.
- SDD verification gate — implementation must pass the repository format/static-check gates.

## Expected behavior

Operations forms preserve the specified TODO/Communication behavior and pass Ruff and mypy.

## Actual behavior

Ruff reported `RUF012`; after that was addressed, mypy reported `Field`/nullable-queryset errors.

## Reproduction

1. Run `make format` or `make check`.
2. Observe failures in `apps/operations/forms.py`.

## Root cause

Django's runtime-generated ModelForm fields are typed generally as `Field`, while the code
used `queryset` without narrowing to `ModelChoiceField`. `Meta.widgets` also lacked the
`ClassVar` annotation required by the configured Ruff rule.

## Resolution

- Annotate both `Meta.widgets` mappings as `ClassVar[dict[str, forms.Widget]]`.
- Narrow `assignee` with `isinstance(..., forms.ModelChoiceField)` before queryset access.
- Handle django-stubs' nullable queryset explicitly, using `User.objects.none()` as the safe
  no-Agent fallback.

## Regression tests

Existing TODO assignee-scope tests remain authoritative; this bug is additionally guarded by
Ruff and mypy in `make check`.

## Spec/design impact

Product spec change: No.

Design update: None.

## Verification

- [ ] `make format`
- [ ] `make check`

Result: static Python compilation passed here; full project checks require the project
dependency environment and remain pending local confirmation.
