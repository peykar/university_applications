# Program Filters

TurkDemy has three levels of program discovery.

## Homepage

Compact filters:
- keyword
- degree
- language
- city
- study-field shortcuts

Keyword/degree/language/city searches redirect to the full Programs catalogue.
Study-field shortcuts link to the dedicated indexable GeneralField landing pages.

## University page

The university is fixed by context. Available filters:
- keyword
- GeneralField
- degree
- language
- academic year
- intake
- currency
- minimum tuition
- maximum tuition
- open/ongoing applications

## Programs page

The complete filter set:
- keyword
- GeneralField
- degree
- language (matches any canonical instruction language)
- study mode
- academic unit
- university
- city
- university type
- minimum/maximum tuition
- currency
- academic year
- intake
- open/ongoing applications
- MOE-approved university
- MOH-approved university
- YÖK-recognized university
- Erasmus+ university

## Offering-level correctness

Tuition, currency, academic year, intake and open/deadline state are
`ProgramOffering` properties derived from canonical offering/fee data.

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

- `field`: canonical GeneralField English slug
- `language`: instruction-language slug
- `study_mode`: stable study-mode enum/code
- `academic_unit`: academic-unit slug
- `university`: university slug
- `city`: city slug
- `degree`: enum/code (already URL-friendly)
- `university_type`: enum/code
- `currency`: ISO-style currency code

Academic year and intake use stable public values when available; otherwise
their UUID primary key remains the reference value.

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
## Reference-model identifiers

Public filters use slugs where the referenced model exposes a stable public slug.
`AcademicYear` and `Intake` currently use UUID primary-key strings in filter URLs.
The filtering service validates those identifiers before applying the corresponding
`_id` lookup.

```python
academic_year_id = state.academic_year
intake_id = state.intake
```

## Catalogue v3 intake and tuition

Current public programme filtering uses canonical `Intake` (`?intake=<uuid>`).
Tuition range and displayed minimum tuition are derived exclusively from active
structured `OfferingFee` tuition/discounted-tuition rows.


## GeneralField landing pages

Curated study fields also have dedicated indexable discovery URLs:

```text
/<locale>/programs/fields/<general-field-slug_en>/
```

The English GeneralField slug is stable across EN/FA/TR/AR route prefixes. These
pages are the canonical SEO surface for a field. The equivalent
`/programs/?field=<slug>` URL remains a `noindex,follow` advanced-filter surface.
