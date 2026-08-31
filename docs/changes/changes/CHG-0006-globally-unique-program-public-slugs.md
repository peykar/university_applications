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
- Canonicalization is idempotent.
- Program localized slugs are globally unique when non-blank.
- Normalized imports may continue supplying source-native program-only slugs;
  TurkDemy canonicalizes them and can still match legacy rows during transition.
- `rebuild_program_slugs` rebuilds existing data and supports `--dry-run`.

## Verification

Regression coverage: `ProgramCanonicalPublicSlugTests`,
`RebuildProgramSlugsCommandTests`, and existing normalized importer tests.
Repository verification uses `make format` and `make check`.
