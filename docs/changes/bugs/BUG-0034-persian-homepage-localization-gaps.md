# BUG-0034 — Persian homepage localization gaps

Status: DONE
Classification: BUG
Owning capability: Application-wide localization (`I18N-001`)

## Report

The Persian public homepage rendered RTL but still showed the dynamic hero summary
in English, study-field cards showed counts without field names, and Latin-script
currency amounts could be visually reordered in RTL presentation.

## Cause

The hero summary used an untrimmed `blocktrans`, so the runtime message shape did
not reliably match the compiled catalogue entry. Study fields were converted to
`values()` dictionaries containing only English name/slug fields while the template
expected a locale-aware model property. Currency amounts were not explicitly bidi
isolated.

## Implementation

- Use `blocktrans trimmed` for the dynamic hero summary so its message id matches
  the existing Persian, Turkish and Arabic catalogue entry.
- Keep the grouped study-field query while carrying representative Persian,
  Turkish and Arabic names via `Max`, and render the dictionary through the
  canonical `localized` template filter with English fallback.
- Wrap popular-program tuition amounts in `<bdi dir="ltr">` so currency/number
  ordering remains stable inside RTL pages.

No translations are fabricated and no catalogue identity, pricing semantics,
permissions, or workflow behavior changes.

## Regression coverage

`tests/test_homepage_localization_regression.py` protects the trimmed dynamic
translation, localized study-field payload/rendering, and bidi-isolated tuition.
