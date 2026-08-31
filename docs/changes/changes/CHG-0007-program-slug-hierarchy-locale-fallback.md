# CHG-0007 — Program slug hierarchy locale fallback

Status: DONE
Classification: CHANGE
Owning capability: catalogue
Requirement: CAT-050

## Request and motivation

Canonical Program slugs include an existing Academic Unit and Department. Some
catalogue hierarchy records are only translated in English. Omitting the hierarchy
component in another locale can collapse distinct Programs to the same public slug.

## Approved behavior

For an existing Academic Unit or Department, canonical hierarchy token resolution is:

1. requested-locale slug;
2. requested-locale name, slugified for that locale;
3. English slug;
4. English name, slugified as ASCII.

A hierarchy component is omitted only when the corresponding structured relation is
absent. No Academic Unit or Department is invented solely for slug generation.
Localized hierarchy data immediately takes precedence once it is populated.

## Implementation

`Program._related_slug_token()` now preserves an existing hierarchy relation through
an English fallback when the target locale has no hierarchy translation.
`rebuild_program_slugs` automatically applies the same canonical rule.

## Verification

Regression coverage exercises both Academic Unit and Department fallback during
normal Program canonicalization and Academic Unit fallback through the rebuild
command. Repository verification remains `make format` followed by `make check`.
