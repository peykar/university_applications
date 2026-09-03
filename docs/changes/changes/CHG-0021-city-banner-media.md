# CHG-0021 — City banner media

Status: VERIFYING
Requested: 2026-09-03

## Request

Allow TurkDemy administrators to upload one banner/picture for a catalogue City and use
it on the public City landing page.

## Classification

CHANGE

## Affected requirements

- `CAT-067` — optional City banner, localized alt text, Admin and public rendering.
- `SEO-017` — representative City image for visible/social/structured metadata.
- `BR-SEO-006` — curated City banner and localized alternative-text policy.

## Desired behavior

- City Admin exposes one optional banner upload and a read-only preview.
- EN/FA/TR/AR alt text can be curated independently of the shared image.
- The active locale alt is used, falling back to English and then the localized City name.
- The City landing page renders a responsive banner only when one exists.
- The same banner becomes the absolute `og:image`, `twitter:image`, and CollectionPage
  `image` value.
- A City without a banner continues to render normally with no invented image.

## SEO review

- Metadata/title/description: unchanged.
- Canonical/hreflang/robots/sitemap: unchanged from CHG-0020.
- Social image: City banner becomes the representative image when available.
- Structured data: CollectionPage gains the same absolute banner URL as `image`.
- Semantic/accessibility: visible banner has localized meaningful alt text.
- Internal links/URL identity/query/pagination: unchanged.
- No-image state: intentionally emits no City-specific image metadata.

## Data/schema note

The repository does not currently track geography migration files beyond
`apps/geography/migrations/__init__.py`. After deploying this code into an existing
database, generate/apply the geography schema change using the project's normal Django
migration workflow before uploading a City banner.

## Verification

- [ ] `make format`
- [ ] `make check`
- [ ] Upload an Istanbul banner in Admin and verify EN + one RTL City landing page.
- [ ] Confirm page source contains the expected `og:image`, `twitter:image`, localized
  `alt`, and CollectionPage `image`.
