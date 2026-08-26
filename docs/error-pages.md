# Error pages

TurkDemy provides a branded `errors/404.html` page for production 404
responses.

Agent Workspace detail views render the same branded page directly when an
applicant or application cannot be found inside the current agent scope. This
also works while `DEBUG=True`, which prevents Django's technical 404 page from
appearing during normal agent workflow testing.

The message is intentionally privacy-safe: the UI does not distinguish between
a resource that does not exist and one that exists under another agent.

The project also registers `handler404 = "apps.core.views.page_not_found"` for
normal production 404s. Django uses custom error handlers when `DEBUG=False`.

## Development behavior

`BrandedNotFoundMiddleware` replaces normal HTML 404 responses with the same
TurkDemy error page even when `DEBUG=True`. This applies to regular browser
routes such as universities, programs, applicant pages, application pages and
unknown site URLs.

The middleware does **not** hide real developer exceptions. Non-404 failures
continue through Django's normal debug/error handling.

API and health endpoints are intentionally excluded so their response formats
remain suitable for machines. Non-HTML 404 responses are also left unchanged.
