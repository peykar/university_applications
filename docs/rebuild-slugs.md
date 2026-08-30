# Rebuild stored slugs

Normal model saves only generate a slug when the slug is blank. This protects stable
URLs. When names/slugs imported historically are stale, use the explicit maintenance
command to intentionally rebuild them from the current names.

Preview first:

```bash
uv run --env-file .env python manage.py rebuild_slugs --dry-run
```

Apply:

```bash
uv run --env-file .env python manage.py rebuild_slugs
```

The command covers the shared localized slug fields (`slug_en`, `slug_fa`, `slug_tr`,
`slug_ar`) and current explicitly mapped slug-like fields such as `FAQCategory.key`.
It uses the same source mapping and Unicode policy as model saves.

Before writing, it computes the complete plan and aborts if regenerated values collide
inside their logical lookup scope. The real operation is atomic. Each target slug is
cleared only on the in-memory model instance and the normal model `save()` method is
called, so there is no intermediate database state containing intentionally blank
slugs. If a related source name is blank, that slug is skipped and its existing value
is preserved.

Because this command intentionally changes existing URLs, run the dry-run first and
review the output. Normal application saves continue to preserve non-empty slugs.
