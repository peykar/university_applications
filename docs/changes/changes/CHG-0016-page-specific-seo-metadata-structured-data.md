# CHG-0016 — Page-specific SEO metadata and structured data

Status: VERIFYING
Requested: 2026-09-03

## Request

Improve page-specific metadata and structured data for Home, Universities,
University Detail, Programs, Program Detail, FAQ, About and Contact.

## Classification

CHANGE under the existing Public SEO capability. This extends the technical SEO
baseline with observable page-specific search/social metadata and schema.

## Requirements

`SEO-010` through `SEO-014`.

## Implementation

- Added localized, page-specific title/meta-description and Open Graph copy for
  all eight requested public surfaces.
- University/Program detail pages use available University banner/logo media for
  social preview images.
- Added safe JSON-LD rendering.
- Added Organization/WebSite, CollectionPage, CollegeOrUniversity,
  EducationalOccupationalProgram, BreadcrumbList, FAQPage, AboutPage and
  ContactPage schema where applicable.
- Schema is built only from existing catalogue/content facts and canonical URLs.
- Added Persian, Turkish and Arabic translations for the new SEO copy and
  rebuilt compiled message catalogues.
- Added behavioral regression coverage in `tests/test_public_page_metadata.py`.
- Added a narrow `RUF001` suppression for an intentional Persian SEO translation assertion; production text and global Ruff policy are unchanged.
- Stabilized metadata tests by explicitly selecting the locale they assert, preventing test-order language leakage.
- Corrected the stabilization to reverse English test URLs inside `translation.override("en")`; setting the language cookie alone cannot control the locale prefix produced by `reverse()` when a prior active translation is Persian.
- Added and compiled the exact `University programs in Türkiye` gettext entry required by the CollectionPage schema in FA/TR/AR.

## Non-goals

- No public URL/slug migration.
- No new keyword/SEO landing pages.
- No fabricated ranking, accreditation, pricing or admission claims.

## Verification

Assistant-side syntax, SDD and static checks are run before packaging.
Project-environment verification remains `make format && make check`.

- Corrected the university-detail metadata assertion to match Django's rendered title text (`&` rather than an assumed `&amp;` serialization).
