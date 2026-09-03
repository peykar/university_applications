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
