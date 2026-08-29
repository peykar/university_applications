# BUG-0011 — University program JSON importer mypy defaults inference

## Status
Fixed.

## Problem
`import_programs_for_university` initialized model update dictionaries from `_localized_defaults()`, whose precise return type is `dict[str, str]`. Mypy therefore inferred each local `defaults` variable as string-valued and rejected the later boolean, related-model, nullable, and integer values that are valid Django model defaults.

## Resolution
The importer now widens each heterogeneous model-default mapping at the assignment boundary to `dict[str, Any]`. `_localized_defaults()` remains precisely typed as `dict[str, str]`; only the dictionaries that are subsequently extended with heterogeneous Django field values are widened.

No import behavior or JSON schema changed.

## Verification
Run:

```bash
make check
```

The regression is fixed when `uv run mypy apps turkdemy` reports no errors for `import_programs_for_university.py` and the remaining checks/tests pass.
