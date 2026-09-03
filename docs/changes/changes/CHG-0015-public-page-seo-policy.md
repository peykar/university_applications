# CHG-0015 — Public-page SEO policy and technical baseline

Status: VERIFYING
Requested: 2026-09-03

## Request

SEO must be considered whenever TurkDemy adds or modifies a public page. Apply
that rule to the repository contract and establish the technical SEO baseline now.

## Classification

CHANGE. This introduces a cross-cutting public-page development invariant and
observable search-engine presentation behavior.

## Decisions

- SEO review is part of the same change as every public-page addition/modification.
- Canonical URLs use the configured `SITE_URL`.
- EN/FA/TR/AR equivalents expose reciprocal hreflang plus English `x-default`.
- Existing public slug behavior remains unchanged in this change.
- Arbitrary search/filter query variants are `noindex,follow`.
- Pagination-only catalogue variants may be indexed and self-canonicalize.
- Root `robots.txt` advertises `sitemap.xml`; it is not a privacy boundary.
- Sitemap includes public static routes plus active Universities/Programs only.
- Page-specific structured data/social-image work remains required whenever
  applicable under the standing SEO gate; unsupported schema is not fabricated.

## Implementation

- Added `BR-SEO-001` through `BR-SEO-003`.
- Added the `docs/specs/seo/` capability (`SEO-001` through `SEO-009`).
- Added an explicit Public-page SEO gate to `AGENTS.md`.
- Added centralized SEO context for canonical/hreflang/robots behavior.
- Added shared canonical, hreflang, robots, Open Graph and Twitter head hooks.
- Added root `/robots.txt` and `/sitemap.xml`.
- Added regression coverage in `tests/test_public_seo.py`.
- Stabilized sitemap alternate-link formatting so the implementation remains within Ruff E501 limits under `make format`.

## Verification

Assistant-side SDD and syntax/static checks are required before packaging.
Final project verification remains `make format && make check` in the project
environment.
