# Program Filters

TurkDemy has three levels of program discovery.

## Homepage

Compact filters:
- keyword
- degree
- language
- city
- study-field shortcuts

These redirect to the full Programs catalogue.

## University page

The university is fixed by context. Available filters:
- keyword
- field/department
- degree
- language
- academic year
- semester/intake
- currency
- minimum tuition
- maximum tuition
- open/ongoing applications

## Programs page

The complete filter set:
- keyword
- field/department
- degree
- language
- university
- city
- university type
- minimum/maximum tuition
- currency
- academic year
- semester/intake
- open/ongoing applications
- MOE-approved university
- MOH-approved university
- YÖK-recognized university
- Erasmus+ university

## Offering-level correctness

Tuition, currency, academic year, semester and open/deadline state are
`ProgramOffering` properties.

TurkDemy applies all selected offering-level conditions to one correlated
`ProgramOffering` query. Thus:

```text
Fall 2026 + tuition <= 8,000
```

only matches a Program when a single offering satisfies both conditions.

## Pagination

Program listings use 24 results per page and preserve all active query-string
filters while navigating pages.

## Filter URL values

Public catalogue URLs use human-readable stable values whenever the model
provides them:

- `field`: department slug
- `language`: program-language slug
- `university`: university slug
- `city`: city slug
- `degree`: enum/code (already URL-friendly)
- `university_type`: enum/code
- `currency`: ISO-style currency code

Academic year and semester use their model slug when available; otherwise
their primary key remains the fallback until those reference models expose
stable slugs.

This keeps URLs readable, shareable and less coupled to database IDs.

## Filter panel behavior

On desktop, the Programs filter sidebar is sticky and independently scrollable.

The action area containing:

```text
Apply filters
Clear all filters
```

is sticky at the bottom of the filter panel, so it remains reachable even when
the complete filter set is taller than the browser viewport.

Filters are submitted as normal GET query parameters. They are not applied
until the user presses **Apply filters**.

On smaller screens, the filter panel returns to normal page scrolling.
