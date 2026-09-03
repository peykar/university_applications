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
