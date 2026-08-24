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
