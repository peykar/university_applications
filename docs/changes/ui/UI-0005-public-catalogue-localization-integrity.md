# UI-0005 — Application-wide localization integrity

Status: IMPLEMENTED  
Classification: UI / localized presentation  
Owning capability: Application-wide localization  
Affected requirement: I18N-001 (APPROVED)

## Finding

The initial finding was visible on Persian public catalogue screenshots: the UI
switched to RTL while substantial interface and model-backed content remained in
English. That screenshot is evidence of a broader application concern, not a
catalogue-only requirement.

Any TurkDemy page that is intentionally translation-enabled can fail in the same
ways. A correct localization pass therefore must cover the complete set of
translation-enabled TurkDemy pages rather than only University/Program pages.

The problem has two distinct sources and they MUST be treated separately:

1. **Interface translation** — static/user-facing copy owned by templates, forms,
   view presentation, helpers, reusable partials, JavaScript presentation, or
   translation catalogues.
2. **Localized structured/domain data** — locale-specific values stored in models
   or supplied by structured application data, such as University/Program names
   and descriptions.

A missing translation in one category MUST NOT be hidden by fixing only the other.

## Observable behavior

For every supported locale and every TurkDemy page intentionally participating in
localization:

- interface copy is rendered in the active locale through the project translation
  system rather than hard-coded English where translation is expected;
- when localized structured/model data exists for the active locale, that value is
  rendered instead of an English value selected unconditionally;
- when a localized structured value is genuinely empty, English MAY be used as the
  canonical fallback; TurkDemy does not fabricate translations;
- RTL locales continue using RTL layout, but direction is treated as a separate
  presentation concern from content localization;
- shared headers, navigation, footers, forms, messages, buttons, badges, filters,
  empty states, pagination, and reusable partials obey the same localization rule;
- proper nouns are not exempt when TurkDemy stores an approved localized value;
- non-language business data keeps its underlying meaning while surrounding labels
  and presentation copy are localized.

## Affected surfaces

The implementation review MUST inventory **all translation-enabled TurkDemy page
families at implementation time**, not just the catalogue. At minimum this means
reviewing the currently applicable:

- public pages: home, about, contact, FAQ, Universities, Programs, details/search;
- authentication/account pages;
- customer Request/workspace pages and related forms;
- customer messaging/inbox/conversation pages;
- translation-enabled agent/staff workspace pages and shared entity components;
- localized error pages;
- global/shared header, navigation, footer and reusable partials used by those
  surfaces;
- both LTR and RTL rendering paths.

A route/template is in scope because TurkDemy intentionally enables localization
for it, not because it belongs to the Catalogue capability.

## Data versus UI boundary

This proposal does **not** authorize generated or guessed translations for missing
structured/domain data. If a requested locale field is empty, the implementation
may fall back to the canonical English value as specified by I18N-001, while the
owning domain's data-audit/cleanup process remains responsible for obtaining and
storing source-backed localized data.

Conversely, translated database content does not excuse hard-coded English UI
copy. Both layers must be correct.

## Acceptance criteria

- [x] Build an inventory of every TurkDemy page family currently intentionally
      translation-enabled and classify its templates/shared partials/helpers.
- [x] English pages remain unchanged in business meaning and remain LTR.
- [x] Persian pages render translatable interface copy in Persian wherever an
      approved translation exists, across every in-scope page family.
- [x] Other supported locales follow the same selection rule; this is not a
      Persian-only fix.
- [x] Localized structured/model values are selected for the active locale when
      populated.
- [x] A deliberately missing localized structured value falls back to English and
      does not render blank or invent a translation.
- [x] Shared navigation, footer, forms, validation/presentation copy, actions,
      badges, filters, pagination and empty states are included in the review.
- [x] Rendered regression tests cover representative public, authentication,
      customer workspace/messaging, and translation-enabled staff/agent surface
      families that exist when implementation begins.
- [x] Tests distinguish interface/UI translation failures from missing localized
      structured-data fallback behavior.
- [x] Existing routes/slugs, permissions, fee semantics, Request flows and
      Application business logic are unchanged.
- [x] RTL pages remain usable after translated strings vary in length.

## Out of scope for this change

- Automatically translating missing domain/catalogue data.
- Cleaning legacy Rasa universities or offerings.
- Changing fee semantics or Application-readiness rules.
- Translating email templates; those remain governed by the email capability and
  Email Preview Gallery requirements.
- Translating Django admin/third-party pages unless TurkDemy has explicitly made
  them part of its localized product UI.
- Redesigning layouts except adjustments necessary to keep localized copy usable.
- Changing URL/slug localization rules.

## Review decision

Approved by product and implemented after the scope was expanded from public Catalogue
pages to every intentionally translation-enabled TurkDemy product surface. The
implementation uses active-locale structured values with English fallback, gettext for
interface copy, localized generated form presentation strings, and server-provided
localized JavaScript labels. No domain-data translations are fabricated.
