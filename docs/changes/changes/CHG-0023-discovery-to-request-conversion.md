# CHG-0023 — Discovery-to-Request conversion and internal linking

Status: VERIFYING
Requested: 2026-09-03

## Request

Audit and improve the public Homepage → City/Field → University → Program → Request journey
so discovery pages do not dead-end and the primary conversion action uses the established
customer-facing Request concept.

## Classification

CHANGE

## Audit findings

- Homepage already links directly to canonical City and GeneralField landing pages.
- City landing pages already expose University and representative Program discovery.
- GeneralField landing pages already expose Program and University discovery.
- University detail already links its City to the canonical City landing page and lists Programs.
- Program detail linked its University but rendered City as plain text and exposed no mapped GeneralField links.
- Program conversion used `Apply / I'm interested`, `Apply / express interest`, and `Continue application`, which conflicts with the customer-facing Request abstraction because Program interest is not yet a formal Application.

## Implemented behavior

- Program City is now a crawlable canonical City landing link when active and routable.
- Active mapped GeneralFields are now crawlable canonical field landing links on Program detail.
- Program detail prefetches GeneralFields to avoid per-field query churn.
- Primary conversion CTA is **Start a Request**.
- Program-interest selection page uses Request terminology while preserving the existing internal route/service and CRQ-091–093 reopen semantics.
- Existing University, related Program, canonical, hreflang, robots, sitemap and structured-data behavior is preserved.

## Affected requirements

- `CAT-069`
- `SEO-019`
- `CRQ-094`
- `BR-SEO-008`

## SEO review

- Canonical/hreflang/robots/sitemap: unchanged for Program detail.
- Internal linking: strengthened with canonical City and GeneralField links.
- Query filters: not promoted.
- Structured/social metadata: unchanged.
- Conversion terminology: Request, not Application, at the Program-interest boundary.

## Stabilization

- Local `make check` reached the full pytest suite with 576 passing tests and one stale structural assertion in `test_apply_program_selector_ux.py`.
- The assertion still expected the superseded customer copy `Who are you applying for?`; it now verifies the canonical Request copy `Who is this Request for?` and explicitly guards against regression to the old phrase.
- This is a CHG-0023 test-alignment correction; no product behavior changed.

## Verification

- [ ] `make format`
- [ ] `make check`
- [ ] Verify Program City and field links in EN/FA/TR/AR.
- [ ] Verify signed-out **Start a Request** authentication handoff.
- [ ] Verify signed-in new/existing/completed Request selection and existing reopen semantics.
