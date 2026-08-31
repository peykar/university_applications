# BUG-0024 — Structured fee display order triggers Ruff RUF012

## Problem

`StructuredFeeSummaryMixin.FEE_TYPE_DISPLAY_ORDER` is an intentionally shared, read-only class-level mapping, but it was left unannotated. Ruff therefore reported RUF012 because the dictionary is a mutable class attribute.

## Fix

Annotate the mapping as `ClassVar[dict[str, int]]`. `ClassVar` was already imported by the admin module, so this is a typing/linting fix only and does not change the semantic fee order or runtime behavior.

## Verification

- Python compilation passes.
- Repository SDD validation passes.
- The user should rerun `make format` and `make check` in the project environment to execute Ruff and the full test suite.
