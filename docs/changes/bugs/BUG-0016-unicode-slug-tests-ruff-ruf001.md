# BUG-0016 — Unicode slug tests trigger Ruff RUF001

## Symptom

`make format` failed because Ruff RUF001 flagged the Turkish dotless `ı` used intentionally
in Unicode catalogue-slug regression fixtures.

## Cause

RUF001 is useful for detecting visually ambiguous Unicode in identifiers and prose, but these
test values intentionally exercise valid Turkish text and localized Unicode slugs.

## Fix

Keep the linguistically correct Turkish fixtures and add narrow `# noqa: RUF001` suppressions
only on the affected test lines. Do not replace `ı` with ASCII `i`, and do not disable RUF001
globally.

## Regression intent

The tests continue to verify that localized catalogue names and slugs preserve native Unicode,
including Turkish dotless `ı`.
