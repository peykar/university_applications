# BUG-0026 — Catalogue v3 UI migration exceeded Ruff line length

## Symptom

`make format` failed in `ruff check . --fix` with E501 errors in the Catalogue v3 UI migration code and its regression fixtures.

## Cause

Several newly added structured-fee expressions and test fixtures were written as single lines longer than the repository's 100-character Ruff limit.

## Fix

Reformatted the affected `ProgramOffering` structured-fee helpers and Catalogue v3 UI/filter test fixtures across multiple lines without changing runtime behavior or test semantics.

## Verification

- A repository-local line-length scan of the affected files reports no lines over 100 characters.
- Python compilation succeeds for all affected Python files.
- Full `make format` / `make check` should be rerun in the project environment where Ruff and project dependencies are installed.
