# BUG-0021 — Rebuild-slugs Turkish fixture triggers RUF001

## Symptom

`make format` failed because Ruff RUF001 flagged the Turkish dotless `ı` in
`Yazılım Mühendisliği`.

## Cause

The character is intentional and linguistically correct Turkish. The regression
test deliberately verifies native Unicode slug generation, so replacing `ı`
with ASCII `i` would weaken the test.

## Fix

Added a narrow line-level `# noqa: RUF001` suppression to the affected fixture.
RUF001 remains enabled globally and the Turkish test data remains correct.
