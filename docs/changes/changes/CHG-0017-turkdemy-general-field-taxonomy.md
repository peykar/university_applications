# CHG-0017 — TurkDemy General Field taxonomy

Status: VERIFYING
Requested: 2026-09-03

## Request

Keep the current University/Program/AcademicUnit/Department catalogue structure,
but add a TurkDemy-wide `GeneralField` classification. TurkDemy admins manually map
Programs after import verification. Public field filtering must use this curated
classification, and the entity must carry multilingual editorial/SEO content for
future field landing pages. `import_programs_for_university` must never perform or
modify this mapping.

## Classification

CHANGE under the existing Catalogue capability. Public filter behavior changes, but
no GeneralField landing page is introduced in this change.

## Requirements

`CAT-053` through `CAT-058`; `BR-CAT-008`; `BR-CAT-009`.

## Implementation

- Added global `GeneralField` with localized names/slugs/descriptions, localized SEO
  title/description, active state and sort order.
- Added optional many-to-many `Program.general_fields` relation and explicit admin
  help text describing manual post-verification curation and interdisciplinary multi-field mapping.
- Added GeneralField administration and exposed Program mapping/filter/search/autocomplete.
- Switched public `field` filtering, field choices and homepage field discovery to
  GeneralField while keeping `Department` intact for University catalogue structure.
- Kept canonical filter identity on `GeneralField.slug_en` across locales.
- `import_programs_for_university` rejects import-provided `general_field` or `general_fields`, leaves new Programs unmapped, and never touches the many-to-many relation so re-import preserves all manual assignments.
- Updated catalogue/domain/business/import documentation and regression coverage.

## SEO review

This change modifies public field-filter behavior and homepage field discovery, so the
public-page SEO gate applies. Arbitrary `?field=` filter URLs remain navigation surfaces
and retain the existing noindex/canonical policy. No new indexable URL is introduced.
GeneralField stores localized editorial and SEO metadata specifically to support a
future dedicated field-landing-page change.

## Non-goals

- No change to University-owned AcademicUnit/Department modeling.
- No automatic field inference or import mapping.
- No GeneralField hierarchy.
- No automatic primary-field inference; all GeneralField memberships are curated manually.
- No public GeneralField landing-page routes yet.

## Database rollout

The repository intentionally does not commit generated Django migrations. After
updating an existing checkout, run the normal `makemigrations`/`migrate` workflow.
The new Program many-to-many relation is optional, so existing Programs remain valid and start
unmapped until manually curated.

## Verification

Run `make format` and `make check` locally after generating/applying migrations in the
normal project workflow. CHG-0017 remains VERIFYING until the user confirms the local
verification result.
