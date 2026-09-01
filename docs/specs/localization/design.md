# Application-wide localization design

Status: IMPLEMENTED
Version: 1.0
Requirement: I18N-001
Change: UI-0005

## Surface inventory

The implementation treats localization as a cross-cutting presentation concern.
The current translation-enabled TurkDemy surface families are:

- public pages: home, about, contact, FAQ, Universities, Programs, search/detail;
- account/authentication pages;
- customer Request/profile/preferences/programs/documents/messages pages;
- customer messaging/inbox/conversation pages;
- Agent/staff applicant, Student, Application, TODO/communication and messaging pages;
- shared base layout, navigation, footer, forms, badges, filters, pagination, empty
  states and reusable partials used by those surfaces;
- localized application presentation/validation messages emitted by views/forms;
- JavaScript presentation owned by TurkDemy and used on those pages.

Email templates remain governed by the email capability and preview-gallery contract.
`templates/admin_tools/`, Django Admin, third-party UI and management-command output are
not part of I18N-001 unless separately promoted to localized product UI.

## Locale-aware structured values

`apps.core.localization.localized_value()` is the canonical read-only selector for
localized structured/model values. It normalizes the active locale to a supported
language code, prefers `<field>_<active locale>`, and falls back to `<field>_en` when
the requested value is empty. It never creates or persists translations.

`LocalizedNameMixin` exposes `localized_name` and `localized_description`. Domain
models with other localized field families expose equivalent properties. A global
`localized` template filter is registered as a template builtin for dictionaries or
objects that do not expose a dedicated property.

Public/product templates must not directly force `name_en`, `description_en`,
`question_en` or `answer_en` for visible translated content. English slugs/identity
fields are not presentation values and remain governed by their own URL contracts.

## Interface copy

Django gettext remains canonical for interface copy. Static template copy uses
`trans`/`translate`/`blocktrans`; Python presentation strings use gettext/lazy gettext.
All supported non-English catalogues contain the literal interface msgids used by the
translation-enabled product surfaces.

Model-generated form labels/help text are a special case because Django can derive
English presentation labels from model metadata. `LocalizedFormMixin` performs a
gettext lookup for generated field labels/help text, model-choice empty labels and
selected presentation widget attributes after normal form initialization. Explicit
lazy translations continue to work unchanged.

## JavaScript presentation

TurkDemy JavaScript must not own hard-coded English presentation fallbacks when the
same component is rendered in translated pages. The searchable multiselect receives
localized placeholder, empty-result and remove-action strings through server-rendered
`data-*` attributes. JavaScript only consumes those values.

## Dynamic/domain content boundary

User-authored free text and source-backed domain content are content, not interface
copy, and are not automatically translated. Approved locale-specific structured model
values are selected when available; missing values fall back to English. Historical
free-text audit/activity descriptions are not machine-translated or rewritten by this
change. Interface labels around those records remain localized.

## Directionality

Existing locale/RTL behavior remains unchanged. RTL is necessary for Persian/Arabic
layout but is not accepted as proof of localization; translated interface copy and
locale-aware structured values are tested independently.

## Compatibility and safety

The change is presentation-only. It does not modify URL/slug identity, permissions,
workflow states, fee semantics, Request/Application behavior, source provenance, or
catalogue import identity. No migration is required.

## Verification strategy

Regression coverage checks:

- active-locale structured value selection and English fallback;
- rendered template translation plus localized structured value in the same render;
- no direct English localized-field forcing in translation-enabled templates;
- complete literal gettext catalogue coverage for Persian, Turkish and Arabic;
- representative surface-family localization markers;
- generated ModelForm labels under an RTL locale;
- JavaScript use of localized server-provided data attributes.
- rendered homepage dynamic `blocktrans` messages use trimmed canonical msgids;
- grouped dictionary-backed localized values retain locale fields and use the canonical
  `localized` selector;
- mixed-direction numeric/currency fragments are bidi-isolated where required.
