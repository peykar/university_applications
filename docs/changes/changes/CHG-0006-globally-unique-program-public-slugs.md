# CHG-0006 — Globally unique Program public slugs

Status: DONE
Classification: CHANGE
Owning capability: catalogue
Requirement: CAT-050

## Request and motivation

Public Program URLs contain one slug segment (`/programs/<slug>/`). Program-only
slugs can collide across universities, making public/API lookup ambiguous. Program
slugs must therefore include the localized University slug.

## Approved behavior

- Each Program `slug_<locale>` is canonicalized as
  `<university.slug_<locale>>-<program-slug-part_<locale>>`.
- Graduate Programs with `thesis_type` include `thesis` or `non-thesis` in the
  program-specific slug, after the degree token when present.
- Canonicalization is idempotent.
- Program localized slugs are globally unique when non-blank.
- Normalized imports may continue supplying source-native program-only slugs;
  TurkDemy canonicalizes them and can still match legacy rows during transition.
- `rebuild_program_slugs` rebuilds existing data and supports `--dry-run`.

## Verification

Regression coverage: `ProgramCanonicalPublicSlugTests`,
`RebuildProgramSlugsCommandTests`, and existing normalized importer tests.
Repository verification uses `make format` and `make check`.

## Structured canonical generation refinement

Program slugs are no longer reconstructed by preserving the historical Program
slug tail. They are generated from localized University slug, localized Program
name, degree, thesis type when applicable, and structured instruction languages.
This makes `rebuild_program_slugs` a true normalization command for legacy rows.



## 2026-08-31 hierarchy extension

CAT-050 now includes the Program's structured Academic Unit and Department in each
localized canonical slug when those relations are present. The order is University,
Academic Unit, Department, Program, degree, thesis type, and instruction language(s).
Missing hierarchy relations are omitted and are never inferred solely for URL generation.
The rebuild command and both catalogue importers preserve transition matching for
pre-hierarchy canonical slugs so existing rows update rather than duplicate.

## 2026-08-31 hierarchy localization hardening

An existing Academic Unit or Department may have incomplete translations. Canonical
slug generation must not silently drop that structured hierarchy component in such a
locale, because doing so can collapse two otherwise distinct Programs to the same
public slug. For hierarchy components only, resolution is now localized slug, then
localized name, then English slug, then English name. A missing hierarchy relation is
still omitted and no hierarchy is invented solely for URL generation.

