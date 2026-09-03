# Application-wide localization

Status: APPROVED
Version: 1.1
Owner: TurkDemy product/platform

## Problem

TurkDemy supports multiple request locales and RTL rendering, but a page can still
be only partially localized: layout direction may change while interface copy or
localized model-backed content remains in English. The problem is not limited to
the public catalogue. Any TurkDemy page that is intentionally translation-enabled
can expose the same inconsistency.

## Goal

Every TurkDemy-rendered page that participates in the project's localization
system should present translatable interface copy and localizable data according
to the active request locale, while using explicit, predictable fallbacks for
missing localized data.

## Actors

- Anonymous visitor
- Customer
- Agent/staff user
- Superuser where a TurkDemy product page is intentionally localized

## Scope

### In scope

- Every TurkDemy-rendered page that is exposed through supported locale-prefixed
  routes or is otherwise intentionally translation-enabled by the application.
- Public pages, authentication/account pages, customer Request/workspace pages,
  messaging pages, translation-enabled agent/staff workspace pages, and localized
  application error pages where applicable.
- Shared navigation, headers, footers, forms, validation/presentation messages,
  labels, actions, badges, empty states, pagination, filters, and reusable partials
  rendered on those pages.
- Localized model-backed content wherever the domain model stores locale-specific
  values, including but not limited to University and Program data.
- Both LTR and RTL supported locales.

### Out of scope

- Machine-readable HTML values required by native controls/semantics (for example `datetime-local` values and `<time datetime>` ISO attributes) remain canonical Gregorian/ISO values; the human-facing text around them uses the localized presentation layer.
- Automatically generating or guessing missing domain-data translations.
- Translating third-party/Django-admin surfaces that TurkDemy has not explicitly
  chosen to localize as product UI.
- Email localization, which remains governed by the email/notification capability.
- Legacy catalogue cleanup, fee/business-rule changes, or slug redesign.
- Visual redesign except adjustments required to keep translated copy usable.

## Requirements

I18N-001 — Translation-enabled page localization integrity

For every TurkDemy-rendered page that is intentionally translation-enabled, the
system MUST render customer/staff-facing interface copy according to the active
request locale through the project translation system instead of hard-coded
English where a translation is expected. When rendered content comes from a
model or other structured source with locale-specific values, the page MUST use
the requested-locale value when present instead of unconditionally selecting the
English value. Layout direction alone MUST NOT be treated as successful
localization. When a requested-locale structured value is genuinely absent, the
page MAY use the canonical English value as a fallback and MUST NOT fabricate a
translation. Shared components and reusable partials MUST follow the same rule as
full pages. Regression coverage MUST exercise representative pages from each
translation-enabled surface family and MUST include at least English and one RTL
locale, distinguishing interface-translation failures from missing localized-data
fallback behavior.

Acceptance criteria:

- Given a page that is intentionally translation-enabled, when a supported locale
  is active, then translated interface copy is used wherever the project has a
  translation for that copy.
- Given localized structured/model data for the active locale, when the page
  renders that data, then the localized value is preferred over English.
- Given a genuinely missing localized structured value, when the page renders it,
  then canonical English may be shown as fallback rather than blank or invented
  text.
- Given an RTL locale, when the page renders, then RTL layout and localized
  content are both correct; RTL direction by itself is insufficient.
- Given a shared component used by multiple translation-enabled pages, when it is
  rendered under a supported locale, then it follows the same localization rules.
- Regression tests cover representative public, account/authentication, customer
  workspace/messaging, and any translation-enabled agent/staff page families that
  exist in the routing/template configuration at implementation time.



I18N-002 — Canonical localized date presentation

The system MUST provide one canonical presentation mechanism for user-visible dates.
The same stored Gregorian date MUST render according to the active locale without
changing the stored value.

I18N-003 — Canonical localized datetime presentation

The system MUST provide one canonical presentation mechanism for user-visible
datetimes, including compact timeline/message variants. Presentation MUST preserve the
existing timezone semantics.

I18N-004 — Persian Solar Hijri presentation

When Persian (`fa`) is active, user-visible Gregorian dates MUST be converted to the
Solar Hijri/Jalali calendar at presentation time. Translating Gregorian month names
without calendar conversion is not sufficient.

I18N-005 — Locale-aware date text and numerals

Human-facing date/datetime output MUST use the approved locale-specific ordering,
month names, punctuation, and numeral system. Persian uses Persian digits and Persian
Solar Hijri month names; Arabic remains Gregorian and uses Arabic-Indic digits.

I18N-006 — Gregorian calendar for EN/TR/AR

English, Turkish, and Arabic user-facing dates remain Gregorian. Their presentation
MUST still follow the active language rather than forcing English date text.

I18N-007 — Timezone-preserving datetime localization

For timezone-aware datetimes, the system MUST apply the existing active/local timezone
before calendar/date formatting. Localization MUST NOT alter the represented instant.

I18N-008 — Date-only safety

Date-only values such as birth dates, passport dates, and programme deadlines MUST
remain date-only during presentation and MUST NOT acquire timezone or time-of-day
semantics.

I18N-009 — Presentation-only compatibility

Existing historical dates/timestamps MUST require no data migration. Sorting,
filtering, APIs, canonical machine-readable values, database values, and business
logic remain unchanged by calendar presentation.

## Business rules / invariants

- Translation completeness of interface copy and localization completeness of
  domain data are separate concerns and must be diagnosed separately.
- Existing approved localized domain values take precedence over English fallback.
- Missing domain-data translations must not be silently fabricated.
- Locale changes must not alter underlying business semantics, identifiers,
  permissions, prices, workflow state, or Request/Application behavior.

## Permissions

Localization does not change authorization. Each page keeps its existing access
rules; this requirement changes only locale-aware presentation and value selection.

## Edge cases

- A page is RTL but still contains English interface copy.
- A template is translated but a view/helper always supplies an English model
  field.
- A localized database field is empty and must fall back to English.
- A reusable partial is translated on one route but hard-coded on another.
- Translation length changes cause clipping or unusable controls.
- Proper nouns have approved localized values in the database and should use them.

## Failure behavior

Missing localized domain data uses the defined fallback rather than producing a
blank page or generated translation. Missing interface translations should remain
visible to tests/audit as localization gaps rather than being masked by unrelated
fallback logic.

## Open decisions

None for the requirement boundary. Concrete surface inventory and test matrix are
design-phase work after product approval.

## Approval

- Product/spec: APPROVED
- Technical design: IMPLEMENTED
