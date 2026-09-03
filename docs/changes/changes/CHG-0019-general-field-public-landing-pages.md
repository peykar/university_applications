# CHG-0019 — GeneralField public landing pages

Status: VERIFIED
Requested: 2026-09-03

## Request

Promote the curated GeneralField taxonomy to first-class public Program discovery
pages, using the agreed entity hierarchy `/programs/fields/<slug>/` rather than a
top-level `/fields/` namespace.

## Classification

CHANGE

## Affected requirements

- `CAT-061`–`CAT-063` — GeneralField public landing routes/content/discovery.
- `SEO-015` — technical SEO contract for the new indexable landing pages.
- `BR-SEO-004` — explicit landing route vs noindex query-filter boundary.

## Desired behavior

- `/en/programs/fields/engineering/` and locale-prefixed equivalents are explicit,
  indexable landing pages.
- The canonical `GeneralField.slug_en` remains the route identity in every locale.
- The page renders localized GeneralField name/description and curated SEO metadata.
- It lists active mapped Programs, paginated 24 at a time, plus Universities offering
  Programs in the field.
- It links to `/programs/?field=<slug>` for advanced filters without changing that
  query route's `noindex,follow` policy.
- Homepage study-field cards point to the dedicated landing page.
- Active mapped GeneralFields are emitted in the multilingual sitemap.
- Structured data is CollectionPage + breadcrumb and uses canonical absolute URLs.

## SEO review

- Metadata: GeneralField localized SEO title/description, with localized content fallback.
- Canonical: dedicated locale-prefixed route.
- Hreflang: EN/FA/TR/AR plus English x-default.
- Robots: index/follow for the clean route; arbitrary query strings remain noindex/follow.
- Sitemap: active GeneralFields with active Programs at active Universities only.
- Social: page-specific OG title/description through template blocks.
- Structured data: CollectionPage and BreadcrumbList only; no unsupported claims.
- Internal links: homepage study fields link to the landing route.
- Duplicate content: query-string field filters remain navigation surfaces, not canonical landing pages.

## Verification

- [x] Python syntax/compile validation in delivery environment.
- [x] SDD traceability updated.
- [x] `make format` locally.
- [x] `make check` locally.
- [x] Manually open at least one EN and one RTL GeneralField landing page.
