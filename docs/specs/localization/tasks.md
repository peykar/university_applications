# Application-wide localization tasks

Status: COMPLETE
Requirement: I18N-001
Change: UI-0005

- [x] `I18N-T01` — Inventory all currently translation-enabled TurkDemy product
      surface families and define the explicit email/Admin/third-party exclusions.
- [x] `I18N-T02` — Add one canonical active-locale structured-value selector with
      English fallback and no generated translation behavior.
- [x] `I18N-T03` — Replace translation-enabled template reads that force English
      localized name/description/question/answer fields.
- [x] `I18N-T04` — Localize view/form presentation messages, activity/event labels,
      filters and generated form presentation metadata.
- [x] `I18N-T05` — Remove hard-coded English presentation fallbacks from TurkDemy
      JavaScript used by translated pages.
- [x] `I18N-T06` — Complete Persian, Turkish and Arabic gettext catalogue entries for
      current literal product-interface strings and compile `.mo` files.
- [x] `I18N-T07` — Add regression coverage for structured fallback, interface
      translation, cross-surface source integrity, form labels and JavaScript.
- [x] `I18N-T08` — Update localization/operator documentation, SDD traceability and
      change history.
- [x] `I18N-T09` — Verify archive integrity, including mandatory `.env.example` and
      exclusion of secret env files, virtualenvs and generated caches.

- [x] `I18N-T10` — Fix rendered-homepage localization gaps for dynamic hero copy,
      grouped study-field names and RTL tuition bidi isolation (`BUG-0034`).
- [x] `I18N-T11` — Keep public catalogue filter identities locale-independent while
      localizing field labels, and prevent inactive catalogue rows from producing
      localized dead-end field links (`BUG-0035`, `CAT-052`).

- [x] `I18N-T12` — Render newly generated workflow system messages from structured event data in the
      active locale while preserving human-authored and legacy stored message text (`CHG-0010`,
      `MSG-010`).
