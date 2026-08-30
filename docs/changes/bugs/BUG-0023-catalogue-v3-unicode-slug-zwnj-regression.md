# BUG-0023 — Catalogue v3 Unicode slug fixture ZWNJ regression

## Status
Fixed

## Problem
The Catalogue v3 branch reintroduced a Persian test slug containing U+200C ZERO WIDTH NON-JOINER (`مهندسی-نرم‌افزار`). Django Unicode `SlugField` validation accepts Unicode letters/numbers, underscores and hyphens, but not ZWNJ, so the normalized-program importer regression test failed during `full_clean()`.

## Fix
The Persian display name remains linguistically correct (`مهندسی نرم‌افزار`). Only the explicit slug fixture and its assertion are normalized to `مهندسی-نرمافزار`, preserving the established catalogue slug policy without weakening validation or silently rewriting imported explicit slugs.

## Verification evidence
User local checks before the fix: SDD, Ruff, formatting, mypy and Django system checks passed; pytest reported 450 passed and this single failing test.
