# Public SEO

Status: BASELINED
Version: 1.2

## Goal

Make technical SEO an invariant of TurkDemy public-page development and provide
a centralized baseline for crawlable multilingual public pages.

## Requirements

SEO-001 — Every public-page addition or modification MUST include an SEO impact
review covering the applicable SEO checklist defined by BR-SEO-001.

SEO-002 — Indexable public routes MUST expose exactly one canonical absolute URL
built from the configured site origin.

SEO-003 — Equivalent EN/FA/TR/AR public routes MUST expose reciprocal `hreflang`
links plus an English `x-default` alternate.

SEO-004 — Public routes with arbitrary search/filter query parameters MUST use
`noindex,follow`; pagination-only URLs MAY remain indexable and MUST self-canonicalize.

SEO-005 — Non-public routes rendered through the shared site template MUST default
to `noindex,follow` unless explicitly approved as indexable public content.

SEO-006 — `/robots.txt` MUST advertise the canonical sitemap location and MUST NOT
be treated as an authorization/privacy boundary.

SEO-007 — `/sitemap.xml` MUST contain indexable static public routes and active
University/Program detail routes, including supported language alternates, and
MUST exclude private workspace routes and inactive catalogue entities.

SEO-008 — The shared public head MUST provide baseline Open Graph URL/site/type
metadata and Twitter card metadata; page-specific public work MUST review whether
more specific social metadata is applicable.

SEO-009 — SEO metadata and crawlability MUST be regression-tested so future public
page work cannot silently omit the repository SEO gate.


SEO-010 — Home, Universities, University Detail, Programs, Program Detail, FAQ,
About and Contact MUST provide page-specific localized titles and meta
descriptions rather than the generic site fallback.

SEO-011 — The same public surfaces MUST provide page-specific Open Graph title
and description metadata; entity detail pages SHOULD use available catalogue
media as their social image.

SEO-012 — Home MUST expose Organization and WebSite structured data; University
Detail MUST expose CollegeOrUniversity and breadcrumb structured data; Program
Detail MUST expose educational-program and breadcrumb structured data using only
facts supported by the catalogue.

SEO-013 — University and Program list pages MUST identify themselves as
CollectionPage structured data; About and Contact MUST identify their page
purpose; FAQ MAY expose FAQPage structured data from the same active questions
visibly rendered on the page.

SEO-014 — Structured data MUST serialize safely as valid JSON, use canonical
absolute URLs, avoid unsupported/invented claims, and remain localized where
human-readable catalogue values are emitted.

## Non-goals

- This baseline does not change existing public slugs.
- It does not create SEO landing pages for arbitrary catalogue filters.
- It does not manufacture structured data where the domain does not support it.
- `robots.txt` is never a substitute for authentication or authorization.


SEO-015 — Curated GeneralField landing pages at
`/programs/fields/<canonical-slug>/` MUST be indexable public pages with canonical
URLs, reciprocal language alternates, English x-default, sitemap inclusion,
page-specific metadata, CollectionPage/breadcrumb structured data, and internal
links from catalogue discovery. Equivalent query-string field filters remain
`noindex,follow`.

SEO-016 — Curated City landing pages at
`/universities/cities/<canonical-slug>/` MUST be indexable public pages with canonical
URLs, reciprocal language alternates, English x-default, sitemap inclusion only when
the City has an active University, page-specific metadata, CollectionPage/breadcrumb
structured data, and crawlable internal links from University detail pages. Equivalent
query-string city filters remain `noindex,follow`.

SEO-017 — When a curated City banner exists, the City landing page MUST use that image as
its visible representative media, Open Graph/Twitter image, and CollectionPage image.
The visible image MUST have locale-aware meaningful alt text. When no City banner exists,
the page MUST omit City-specific image markup and MUST NOT invent a social image.


SEO-018 — The homepage City discovery surface MUST provide crawlable direct links to the
canonical indexable City landing routes. It MUST NOT promote query-string city filters as
canonical destination pages. Reusing a curated City banner on a homepage destination card
MUST preserve locale-aware meaningful alt text. Existing homepage canonical, hreflang,
robots, sitemap identity, social metadata, and structured data remain unchanged.
