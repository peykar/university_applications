# Public SEO — technical design

Status: BASELINED

- `apps.public.context_processors.seo` centralizes canonical URL, language
  alternates and robots policy from the resolved route.
- `templates/base.html` renders canonical, hreflang, robots and baseline social
  metadata from that context.
- Canonical absolute URLs use `settings.SITE_URL`, not an untrusted request host.
- Pagination-only query strings self-canonicalize. Other query-string variants
  are `noindex,follow` until promoted to explicit SEO landing routes.
- `apps.public.seo_views` owns root-level `robots.txt` and `sitemap.xml`.
- The sitemap contains static public routes plus active University and Program
  detail routes and their supported language alternates.
- Existing public detail routing continues to use the established `slug_en`
  route identity. Localized-slug migration is intentionally out of scope.

## Development gate

Any task touching a public template/view/route must review SEO-001 and record the
applicable SEO effects in its change record and tests.


## Page-specific metadata and structured data

- Requested public templates own their localized title, description and social
  copy so metadata follows the same translation catalogue as visible content.
- `apps.public.seo` provides canonical absolute URL, breadcrumb and graph helpers.
- Public views build structured data from the same domain objects rendered on the
  page; no SEO-only domain facts are invented.
- `apps.public.templatetags.seo.json_ld` safely serializes schema payloads.
- University/Program detail pages prefer available University banner/logo media
  for Open Graph/Twitter images.


## Curated GeneralField landing pages

- GeneralField landing URLs live under the Program catalogue namespace:
  `/programs/fields/<slug_en>/`.
- `slug_en` is intentionally stable across locale-prefixed routes, matching the
  existing canonical filter identity policy.
- The dedicated route is indexable; `/programs/?field=<slug_en>` remains a
  noindex filter/navigation URL and is used for deeper advanced filtering.
- Active mapped GeneralFields are emitted in the multilingual sitemap.
- Homepage study-field cards link directly to the dedicated landing pages.

## Curated City landing pages

- City landing URLs live under the University catalogue namespace:
  `/universities/cities/<slug_en>/`.
- `slug_en` remains stable across locale-prefixed routes.
- The clean City route is indexable; query-string city filters remain
  `noindex,follow` navigation surfaces.
- The multilingual sitemap emits only active Cities with at least one active
  University.
- University detail pages link their City label to the dedicated landing page.



## CHG-0021 City representative image

City landing pages use `City.banner` as the single curated representative image when it
exists. The view converts its media URL to an absolute URL for `og:image`,
`twitter:image`, and CollectionPage `image`. The template uses
`City.localized_banner_alt` for visible alternative text. Missing banners remain a clean
no-image state; there is no generated or unrelated fallback image.

## Homepage City internal linking (SEO-018)

The homepage includes a Study destinations section for up to five qualifying Cities. Each
card is an ordinary crawlable anchor to `/universities/cities/<slug_en>/`, strengthening
internal discovery of the dedicated City SEO surface without changing homepage canonical
identity or promoting `/programs/?city=...` filter URLs. Curated City banners retain their
localized alternative text when reused on the homepage.
