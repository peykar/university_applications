# CHG-0020 — City public landing pages

Status: VERIFIED
Requested: 2026-09-03

## Request

Promote catalogue Cities to first-class public University discovery pages using the
agreed hierarchy `/universities/cities/<slug>/`, with the same public-page SEO contract
already applied to GeneralField landing pages.

## Classification

CHANGE

## Affected requirements

- `CAT-064`–`CAT-066` — City public landing routes/content/discovery.
- `SEO-016` — technical SEO contract for the new indexable landing pages.
- `BR-SEO-005` — explicit City landing route vs noindex query-filter boundary.

## Desired behavior

- `/en/universities/cities/istanbul/` and locale-prefixed equivalents are explicit,
  indexable landing pages when the City is active and has an active University.
- The canonical `City.slug_en` remains the route identity in every locale.
- The page renders localized City name/description and curated SEO metadata.
- It lists active Universities, paginated 24 at a time, and up to 12 representative
  active Programs from active Universities in the City.
- It links to `/programs/?city=<slug>` for advanced Program discovery without changing
  that query route's `noindex,follow` policy.
- University detail pages link their City label to the dedicated landing page.
- Qualifying Cities are emitted in the multilingual sitemap.
- Structured data is CollectionPage + breadcrumb using canonical absolute URLs.

## SEO review

- Metadata: City localized SEO title/description, with localized content fallback.
- Canonical: dedicated locale-prefixed route.
- Hreflang: EN/FA/TR/AR plus English x-default.
- Robots: index/follow for the clean route; arbitrary query strings remain noindex/follow.
- Sitemap: active Cities with at least one active University only.
- Social: page-specific OG title/description through template blocks; a City-specific social image is not applicable because City has no canonical media field, so no image is invented.
- Structured data: CollectionPage and BreadcrumbList only; no unsupported claims.
- Semantic crawlability: one localized H1, visible City editorial copy, University/Program card content, and existing meaningful catalogue image alt text.
- Internal links: University detail City labels link to the landing route.
- Duplicate content: query-string city filters remain navigation surfaces, not canonical City pages.
- Pagination: pagination-only query strings retain the shared self-canonicalizing policy.
- Modified University detail pages: only the visible City label gains a crawlable City link; their existing metadata, canonical/hreflang, indexability, sitemap identity, social metadata, and structured data remain unchanged.

## Verification

- [x] User verified CHG-0020 behavior.
- [x] City landing page and sitemap behavior accepted.
