# BUG-0014 — Turkish fixture text triggered Ruff ambiguous-character checks

## Status

Fixed.

## Symptom

`make format` stopped in `ruff check . --fix` with `RUF001` for legitimate Turkish dotless `ı` characters in `tests/test_university_data_dump.py`.

## Cause

The university dump regression fixture intentionally contains real Turkish localized text. Ruff correctly flags visually confusable Unicode characters by default, but replacing Turkish `ı` with ASCII `i` would corrupt the locale fixture and weaken the export test.

## Fix

The two intentional Turkish fixture lines now carry narrow `# noqa: RUF001` suppressions. The localized strings remain linguistically correct and the rule remains enabled everywhere else.

## Verification

Run:

```bash
make format
make check
```
