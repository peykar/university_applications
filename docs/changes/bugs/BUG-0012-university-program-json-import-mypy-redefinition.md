# BUG-0012 — University program JSON importer mypy local redefinition

## Status
Fixed

## Problem
`make check` reached mypy and reported `Name "defaults" already defined` in
`import_programs_for_university.py`. Both the academic-unit and department loops
inside `_import_payload()` used an annotated local named `defaults`. Python loop
blocks do not introduce a new scope, so mypy's `no-redef` check correctly treated
the second annotation as a redefinition in the same function.

## Resolution
Use descriptive, independently typed locals:

- `academic_unit_defaults`
- `department_defaults`

The change is type-checking-only and does not alter importer behavior, JSON
schema, lookup keys, update semantics, or persistence.

## Verification
Repository syntax compilation and the SDD validator pass. Run `make check` in
the project development environment to verify the full quality suite including
mypy and tests.
