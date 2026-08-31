# BUG-0028 — Structured Program slug import idempotency

Status: DONE
Classification: BUG
Owning capability: catalogue
Requirement: CAT-050

## Problem

After CAT-050 made Program public slugs deterministic from structured data, two
regressions remained in verification. Tests still asserted the previous
historical/explicit slug contract, and a schema-v2 programme re-import could
create a duplicate when the Program display name changed because the persisted
canonical slug changed while the source `slug_en` remained stable.

## Resolution

- Program slug regression tests now assert the CAT-050 structured contract.
- The normalized programme importer continues treating input `slug_en` as the
  stable source identity for re-imports.
- Before upsert, the importer reconstructs the canonical slug that the stable
  source identity would have produced from degree, thesis type, and instruction
  languages, and includes that value among transition lookup candidates.
- A display-name change therefore updates the existing Program instead of
  creating a duplicate, while the persisted public slug is rebuilt from the new
  structured display data.

## Verification

Covered by `UniversityProgramJsonImportTests` and
`LocalizedSlugAutogenerationTests`, with repository verification through
`make format` and `make check`.
