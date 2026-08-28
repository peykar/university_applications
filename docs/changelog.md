- Scoped the Request-card no-hover regression test to Request-card selectors; unrelated catalogue hover animations remain valid.
- Fixed My Requests program labels and removed request-card hover visual effects.
- Replaced brittle Django-template branch parsing in the customer Request terminology test with explicit assertions for the customer navigation links.
- Fixed the customer Request terminology regression test to use the existing `request_nav` fixture when isolating the customer navigation branch.
- Corrected the remaining customer-redesign source-inspection tests: customer entity-navigation scoping and finalized Request document wording.\n- Aligned legacy customer workspace tests with the My Requests redesign: customer-only terminology scope, Request document wording, and the menu-only sidebar contract.\n- Redesigned the customer workspace around a single **Request** abstraction: menu-only sidebar, My Requests landing page, Find Programs action, request cards with contact/program details, Agent suggestion tips, and unread-message/document-replacement attention indicators.
- Added optional `WHATSAPP_NUMBER` configuration for the customer sidebar and linked Get Help to the existing Contact page.
- Fixed the final legacy internal-notes test so it scopes inspection to AgentLeadEditForm and excludes StudentRecordConversionForm.
- Corrected the remaining legacy source-inspection tests after Create Student Record: Lead edit-form note isolation and Student full_clean phone-validation contract.
- Fixed legacy source-inspection tests for the Create Student Record workflow after the finalization redesign.
- Aligned legacy finalization regression tests with the SDD-defined Create Student Record workflow: zero discussed programs are valid, Student notes are separate from Lead profile notes, and Student model validation owns phone validation.\n
## 2026-08-28 — Create Student Record conversion workflow

- Fixed static typing in the conversion view by explicitly narrowing nullable offerings and preserving `LeadProgramInterest` types during program selection.
- Replaced the Agent finalization modal with a dedicated **Create Student Record** page.
- Student fields are prefilled from the Lead and editable before conversion.
- All Lead documents are selectable; verified documents default on, selected unverified documents are approved and transferred, and unchecked verified documents remain verified but are not copied.
- Zero or more discussed programs may be selected; every selected program requires an active offering and creates a DRAFT Application.
- Removed persistent `LeadProgramInterest` → `Application` coupling while preserving the existing LeadDocument → StudentDocument conversion bridge.
- Expanded applicant-finalization SDD through `FIN-017` and kept conversion database changes atomic.
# Changelog

## Applicant finalization creates optional initial draft applications
- The responsible Agent may select zero or more discussed programs during finalization.
- Selecting no program still creates/reuses the Student and finalizes the Lead without creating Applications.
- Customer-added and Agent-suggested program interests are both eligible.
- Program-level interests require an active intake/offering selection.
- Selected interests become linked DRAFT Applications in the same atomic Student finalization operation.
- Removed Django admin bulk finalization because it cannot collect the required per-program choices.

## Current baseline

### Project structure
- Converted the initial reusable app into a complete runnable Django project.
- Uses `uv` for dependency/environment management.
- SQLite is the zero-configuration development database.

### Phone handling
- Added `phonenumbers`.
- Added phone validation and E.164 normalization.
- Added `User.cell_verified_at`.

### Student residence
- Changed `Student.city_of_residence` from a `City` foreign key to free text.

### Audit fields
- Changed `created_by` and `updated_by` to use `related_name="+"`.
- No reverse audit relations are created on the user model.

### Documentation
- Added canonical `docs/` folder.
- Documentation must be updated as part of relevant future changes.

### Agent organizations
- Changed `Agent` from a one-to-one user profile to an organization/company.
- Added required `company_name`.
- Added optional `logo`.
- Replaced the single `user` relation with many-to-many `users`.
- Preserved parent/sub-agent hierarchy.

### Agent contacts and documents
- Added optional agent email and website.
- Added optional agent cell/mobile and landline phone numbers.
- Agent phones use the existing validation and E.164 normalization layer.
- Added `AgentDocument` with name, internal description and uploaded file.
- Agent documents use agent-specific upload paths.

### Model field help text
- Added explanatory `help_text` to domain-specific fields where the field name
  alone may not make the business meaning clear.
- Documented the requirement to add help text for acronyms, regulatory flags,
  specialized pricing/admission fields, and other ambiguous model fields.

- Added descriptions for YÖK/MOE/MOH recognition, Erasmus and dormitory flags.
- Added descriptions for QS/THE/ARWU/URAP ranking fields.
- Added descriptions for offering fee basis, tuition variants, discounts, quota and deadline.

### Approval field scope
- Removed `is_moe_approved` from `Program`.
- Removed `is_moh_approved` from `Program`.
- Kept YÖK, MOE, and MOH recognition/approval strictly on `University`.

### Listing priority
- Added indexed `listing_priority` to `University`.
- Added indexed `listing_priority` to `Program`.
- Default is `0`; higher values indicate greater internal listing priority.
- Chose the explicit name `listing_priority` instead of RasaStudy's
  `boost_score`.

### High-school GPA help text
- Added explanatory help text to `Student.high_school_gpa`.
- Added explanatory help text to `Student.high_school_gpa_scale`.

### Country reference data
- Added `pycountry` and `Babel`.
- Added idempotent `populate_countries` management command.
- ISO2/ISO3 come from ISO 3166-1 via `pycountry`.
- English, Persian, Turkish and Arabic names come from CLDR via Babel.
- Added tests and documentation for country population.

### FAQ/contact merge from tgate
- Reworked and added `FAQCategory`, `FAQ`, and `ContactSubmission` from the previous `tgate` project.
- Added English/Persian/Turkish/Arabic FAQ localization with fallback helpers.
- Replaced the old stored FAQ category count with dynamic `faq_count`.
- Added E.164 phone handling to contact submissions.
- Fixed `Agent` duplicate `__str__()` and `clean()` definitions by consolidating each behavior into one method.
- Fixed adjacent Django admin registration/filter issues found while validating the merged project.

### TurkDemy multi-app refactor
- Renamed the project to TurkDemy.
- Replaced the monolithic `university_applications` app with domain apps.
- Added `accounts`, `agents`, `geography`, `universities`, `students`,
  `applications`, `content`, `health`, and shared `core`.
- Split Django settings into base/local/production.
- Added health/readiness endpoints.
- Added `data/rasa/` and `data/fixtures/`.
- Added Dockerfile, docker-compose, Makefile, `.python-version`, and pre-commit config.

### Linting and code-quality toolchain
- Added Black.
- Expanded Ruff rules, including Django-specific checks and import sorting.
- Added mypy and django-stubs.
- Added pytest coverage tooling.
- Added pre-commit hooks.
- Added Makefile targets for linting, formatting, typing, tests and the complete quality gate.
- Fixed the pytest Django settings path after the TurkDemy project rename.

### Rasa FAQ downloader
- Added `scripts/download_rasastudy.py` to TurkDemy.
- Downloader now exports FAQ categories and FAQs in addition to universities
  and programs.
- FAQ endpoint variants are auto-detected by response shape.
- FAQ assets such as `audio_url` are included in asset discovery/download.
- Added `make rasa-download`.

### Rasa management-command importers
- Added `import_rasa_catalogue`.
- Added `import_rasa_content`.
- Added aggregate `import_rasa_data`.
- Rasa flattened program fees are mapped into `ProgramOffering`.
- Rasa `boost_score` maps to TurkDemy `listing_priority`.
- Added importer tests and Makefile targets.

### Rasa university media import
- Catalogue importer now reads `assets_manifest.json`.
- University logo assets populate `University.logo`.
- University banner/cover assets populate `University.banner`.
- Additional university image assets populate `UniversityMedia`.
- Media is saved through Django storage APIs.
- Added `docs/rasa-mapping.md` as the canonical mapping reference.

### Admin operations upgrade
- Added shared `AuditAdminMixin` and active/inactive actions.
- Added rich admin configuration across accounts, agents, geography,
  universities, students, applications, and content.
- Added university logo/banner previews and media inline.
- Added program-offering inline.
- Added student-document and application-document inlines.
- Added application status actions and document verification actions.
- Added contact handled/unhandled actions.
- Added TurkDemy admin branding.
- Added `docs/admin.md`.

### Configurable system audit user
- Added shared system-user audit helpers in `apps/core/audit.py`.
- System username/email/permissions are configurable through `.env`.
- Added `python-dotenv` for `.env` loading.
- System user defaults to inactive, non-staff and non-superuser with an unusable password.
- Rasa imports and country population now set `created_by`/`updated_by` consistently.
- Re-imports preserve the original `created_by` while changing `updated_by` to the system actor.
- Added `ensure_system_user` management command and audit tests.

### Production/full-stack foundation
- Added `DATABASE_URL` support through `dj-database-url`.
- Added PostgreSQL/psycopg support.
- Added Gunicorn.
- Added development and production Docker Compose files.
- Added database-aware readiness checks.
- Enabled Django password validators.
- Enabled LocaleMiddleware, explicit EN/FA/TR/AR languages and locale paths.
- Added environment-configured CSRF trusted origins.
- Added Django REST Framework and CORS support.
- Added initial public forms, views and server-rendered pages.
- Added a separate React/TypeScript/Vite frontend.
- Added `.dockerignore` and `.editorconfig`.

### Canonical site URL and email configuration
- Added environment-driven `SITE_URL`.
- Added shared absolute URL helpers for emails/notifications/background tasks.
- Added environment-driven Django SMTP/email configuration.
- Added shared email sending helper.
- Updated `.env.example`.
- Added `docs/site-url-and-email.md`.

### Pillow runtime dependency
- Added Pillow as a runtime dependency because TurkDemy uses Django `ImageField`
  for agent logos, university logos/banners, and university media images.

### Dependency audit and runtime fixes
- Audited third-party Python imports against `pyproject.toml`.
- Added missing Babel runtime dependency required by country localization.
- Ensured Pillow remains a runtime dependency for Django `ImageField`.
- Added explicit `phonenumbers` because project code imports it directly.
- Restored the complete development toolchain dependencies.
- Rebuilt `pyproject.toml` as valid TOML and added `docs/dependency-audit.md`.

### Rasa numeric parsing fix
- Added tolerant integer parsing for Rasa values serialized as decimal strings.
- `duration_years="5.0"` now imports as `Program.duration=5`.
- Applied the same normalization to `boost_score` and `quota`.
- Added regression coverage for decimal-string integer values.

### Make bootstrap target
- Added the previously documented but missing `make bootstrap` target.
- Added `setup`, `migrate`, `system-user`, and `countries` targets.
- Documented the fresh-checkout bootstrap and Rasa import workflow.

### Rasa FAQ category mapping fix
- Fixed FAQ imports for the actual Rasa payload shape where `FAQ.category` is
  a string such as `خوابگاه` matching `FAQCategory.key`.
- Added defensive support for numeric IDs, explicit keys, and nested category objects.
- Added regression coverage for string-based FAQ-category mapping.
- Rebuilt the Makefile with one canonical definition per target, removing
  duplicate-target warnings.

### Django-template frontend consolidation
- Removed the separate React/Vite frontend.
- Made Django templates the canonical public website architecture.
- Removed frontend Docker/Makefile/build configuration.
- Simplified production Compose to PostgreSQL + Django/Gunicorn.
- Fixed static asset loading through Django `{% static %}` and
  `STATICFILES_DIRS`.
- Added responsive public templates for university/program catalogue,
  university/program details, FAQ and contact.
- Added a language selector and RTL layout direction for Persian/Arabic.
- Kept Django REST Framework as an optional API/integration layer.
\n### TurkDemy brand assets
- Added native SVG primary, horizontal, emblem and monochrome logo variants.
- Added favicon ICO/PNG, Apple Touch, Android/PWA icons and web manifest.
- Integrated branding into the Django base template.
- Added `docs/branding.md`.

### Header logo rendering fix
- Made the TurkDemy header brand insertion robust.
- Ensured the base template loads Django static tags.
- Strengthened header/logo layout rules so the SVG cannot collapse or disappear.
- Added a direct static-asset verification URL to the branding docs.

### Homepage experience redesign
- Added hero catalogue search and live catalogue statistics.
- Added featured-university cards with program counts and recognition metadata.
- Added study-field discovery and tuition-aware popular program rows.
- Added process, trust, FAQ preview, CTA and richer footer sections.
- Uses imported university banner media for the hero when available.
- Added `docs/homepage.md`.

### Phone validator import fix
- Changed phone validation to import `phonenumbers.phonenumberutil` primitives
  directly instead of relying on top-level `phonenumbers` re-exports.
- Added regression tests for international/E.164 validation and the public
  contact form.
- Added `check_phone_library` / `make phone-check` diagnostics to show exactly
  which `phonenumbers` module Python loads.

### Phone backend compatibility fix
- Removed direct imports from `phonenumbers` implementation modules.
- Phone parsing now uses `django-phonenumber-field`'s public `PhoneNumber` API.
- Standardized runtime dependency on
  `django-phonenumber-field[phonenumberslite]`.
- Removed the explicit `phonenumbers` dependency to avoid mixed/ambiguous
  phone-number backends.
- Updated `make phone-check` and regression tests.

### Core app registration fix
- Registered `apps.core` in `INSTALLED_APPS` using `CoreConfig`.
- This makes core management commands such as `check_phone_library`
  discoverable by Django.
- Ensured the core management-command package structure is complete.

### Program catalogue filtering
- Added compact homepage filters for keyword, degree, language and city.
- Added university-page filters for field, degree, language, tuition, currency,
  academic year, semester and open/ongoing applications.
- Added full Programs catalogue filters including university/city/type,
  university recognition flags and Erasmus+.
- Offering-level filters use one correlated ProgramOffering match.
- Added 24-item pagination with filter preservation.
- Added filter regression tests and `docs/program-filters.md`.

### Slug-based catalogue filters
- Replaced public filter IDs with slugs for university, city, language and
  department/field.
- Homepage study-field links now use department slugs.
- Kept natural enum/code values for degree, university type and currency.
- Academic-year/semester IDs are retained only when their models do not expose
  slugs.

### Program filter sidebar usability
- Made the desktop Programs filter sidebar independently scrollable.
- Added a sticky bottom action area so `Apply filters` and `Clear all filters`
  remain accessible.
- Added a short instruction explaining that filters are applied on submit.
- Kept normal page scrolling behavior on smaller screens.

### Rich program detail page
- Rebuilt program detail as a richer decision page.
- Added university banner/logo/media and university recognition/context.
- Replaced the simple offerings table with tuition/intake cards.
- Added deadline open/closed status and extra pricing/deposit fields.
- Added similar-program ranking across the catalogue.
- Added more programs from the same university.
- Added a sticky guidance/contact card.
- Added `docs/program-detail.md`.

### Applicant / Lead workflow
- Added dedicated `leads` Django app.
- Added multiple Leads per authenticated account.
- Added broad study preferences and program recommendation flag.
- Added user/agent/system program interests and suggestions.
- Added provisional Lead documents with verification/conversion links.
- Added per-Lead conversation, messages, attachments and read receipts.
- Added Lead activity history.
- Added deterministic system recommendation service.
- Added explicit Lead finalization and transactional Student conversion.
- Qualified program interests can become formal Applications.
- Changed `Student.user` from one-to-one to many-students-per-account ownership.
- Added customer Applicant workspace and login-required Apply flow.
- Added staff Admin actions for recommendations, finalization and conversion.
- Added workflow tests and documentation.

### Lead audit helper import fix
- Fixed Lead services to import `get_system_user` from the project's canonical
  `apps.core.audit` module.
- Added `apps.core.services.audit` as a backward-compatible re-export so older
  local imports do not break.
- Updated affected tests to use the canonical audit helper.

### Repository-wide lint cleanup
- Fixed the Ruff issues reported by `make check`, including line length, import ordering,
  unused imports, simplification rules, mutable class attributes, and redundant noqa markers.
- Cleaned the newly added Leads workflow files as well as existing accounts, agents,
  applications, content, geography, students, universities, scripts, tests, and settings.
- Preserved the country-population locale map while reorganizing its imports.

### Pre-commit mypy and Lead constraint fix
- Fixed `LeadMessageRead.Meta.constraints` so the single
  `UniqueConstraint` is stored in a one-item tuple.
- Changed the pre-commit mypy hook to run through the project's `uv`
  environment instead of pre-commit's isolated mypy virtualenv.
- Pre-commit mypy now uses the same command scope as project checks:
  `uv run mypy apps turkdemy`.
- This prevents missing runtime dependencies such as `dj-database-url`
  inside the mypy Django plugin bootstrap.

### Mypy cleanup
- Fixed nullable relationship narrowing in lead conversion, program validation, and public program views.
- Fixed Django form field/widget typing without disabling type checking.
- Fixed admin mixin/action typing and prepopulated field annotations.
- Fixed URL pattern typing and Rasa importer optional-result narrowing.
- Offering filters now resolve academic year and semester by slug instead of passing slugs to UUID foreign-key lookups.

### Documentation formatter fix
- Updated the Python example in `docs/model-field-guidelines.md` to match
  Ruff's formatter output, so `ruff format --check .` does not fail on the
  documentation snippet.

### Program filter test alignment
- Updated Semester filter tests to use primary-key strings because Semester
  currently has no slug field.
- Kept slug-based filtering for reference models that actually expose slugs.

### Program offering filter implementation fix
- Fixed `apply_program_filters()` to stop querying `Semester.slug_en`, which
  does not exist.
- Semester filters now use the current Semester primary key.
- AcademicYear uses the same primary-key fallback when no slug field exists.
- Kept public templates and tests aligned with the same contract.

### UUID-safe offering filters
- Parse AcademicYear and Semester query-string values to `UUID` before using
  Django `_id` lookups.
- Invalid UUID filter values now produce an empty queryset instead of a
  database/type error.
- Formatted the Python example in `docs/program-filters.md` for Ruff.

### UUID filter type narrowing
- Moved AcademicYear/Semester UUID parsing into the guarded offering-filter
  branches.
- `_id` lookups now receive a statically narrowed `UUID`, satisfying
  django-stubs for non-nullable foreign keys.

### Unified authentication with django-allauth
- Added Google and Telegram social login.
- Added passwordless email signup/login with one-time codes.
- Replaced Django auth URLs with django-allauth.
- Kept provider callback URLs outside i18n prefixes.
- Added environment-driven provider credentials.
- Added TurkDemy authentication templates and styling.
- Added Telegram identity synchronization to existing User fields.
- Added `docs/authentication.md`.

### Allauth settings mypy annotation
- Explicitly typed `SOCIALACCOUNT_PROVIDERS` as
  `dict[str, dict[str, Any]]`.
- This allows environment-dependent `APP` provider configuration to be added
  without mypy treating nested provider values as generic `object`.

### Reverse-proxy HTTPS callback fix
- Added `SECURE_PROXY_SSL_HEADER` for `X-Forwarded-Proto`.
- Enabled `USE_X_FORWARDED_HOST`.
- Social authentication callbacks now use the public HTTPS scheme behind Nginx.

### Ruff-only formatting
- Removed Black from the development dependencies and pre-commit hooks.
- Removed Black from `make format`, `make format-check`, and `make check`.
- Ruff is now the single code formatter; Ruff linting remains enabled separately.


### Skip duplicate email verification after social login
- Set `SOCIALACCOUNT_EMAIL_VERIFICATION = "none"`.
- Google login no longer triggers a second TurkDemy email verification code.
- Direct email signup/login remains mandatory-verification/passwordless.
- Added a regression test for the configuration split.

### Preserve existing passwords during Google email linking
- Added `TurkDemySocialAccountAdapter`.
- Verified Google email is synchronized into allauth's `EmailAddress` table
  before social email authentication is accepted.
- Existing usable passwords are preserved when Google is linked by verified
  email.
- Existing `is_staff` and `is_superuser` flags remain untouched.
- Added regression coverage for legacy admin accounts.

### Account sign-in method management
- Added `/accounts/settings/sign-in-methods/`.
- Added Google and Telegram `process="connect"` workflows.
- Added manual email attachment + allauth verification flow.
- Added verified-primary-email management.
- Added Google/Telegram disconnect actions.
- Prevented users from removing their last usable sign-in method.
- Added conflicts checks for email addresses already owned by another account.
- Added tests and account-security styling.

### Allauth email confirmation API compatibility
- Replaced the removed `allauth.account.utils.send_email_confirmation` helper.
- Manual login-email verification now calls `EmailAddress.send_confirmation()`.
- Added regression coverage for the add-email verification flow.

### Email confirmation mock assertion fix
- Corrected the sign-in-method regression test for the bound
  `EmailAddress.send_confirmation()` call.
- The mocked method records the request keyword argument without exposing
  the model instance in `call.args`.

### Google verified-email synchronization
- Google `email_verified=true` now synchronizes to allauth `EmailAddress`.
- Matching Google emails become verified and primary when appropriate.
- Added `sync_social_emails` to repair existing connected Google accounts.
- Sign-in methods now distinguishes verified email login from pending email.
- Added conflict protection and regression tests.

### Canonical TurkDemy social connection UI
- Successful Google/Telegram connect flows return to Sign-in methods.
- `/accounts/3rdparty/` redirects to TurkDemy's canonical connection page.
- Added styled safety-net overrides for allauth connection/email/password pages.
- Added regression tests for connection redirects.

### Authentication provider icons
- Replaced text `G`/`T` placeholders with Google and Telegram SVG icons.
- Added a consistent email SVG icon.
- Updated the login page and Sign-in methods page.
- Added regression coverage for provider icon rendering.

### Complete authentication translations
- Added Persian, Turkish and Arabic translations for login/OTP/account-security UI.
- Added project locale catalogues and compiled `.mo` files.
- Wrapped account forms and success/error messages in Django gettext.
- Added regression tests for authentication translations.

### Ruff Unicode translation-test exception
- Added a per-file `RUF001` ignore for `tests/test_auth_translations.py`.
- Legitimate Turkish dotless `ı` characters remain unchanged in exact
  translation assertions.

### Fix gettext alias shadowing
- Renamed the `get_or_create()` throwaway boolean in `add_login_email()`.
- Prevented the gettext `_` alias from being overwritten by a boolean.
- Added regression coverage for translated add-email success messaging.

### Global RTL support
- Added language-aware `lang` and `dir` attributes to the root HTML element.
- Persian and Arabic now render RTL; English and Turkish remain LTR.
- Added RTL-aware shared layout rules for navigation, auth pages and account cards.
- Protected emails/usernames with LTR bidi isolation.
- Added regression tests for language direction.

### Programs catalogue visual redesign
- Rebuilt the public Programs page as a wider discovery experience.
- Added a sticky, polished filter panel without changing filter semantics.
- Added university logos, stronger program hierarchy and richer metadata.
- Redesigned tuition and detail actions for clearer scanning.
- Improved empty state, pagination spacing, responsiveness and RTL behavior.

### Programs filter balanced layout
- Restored all Program filters to always-visible controls.
- Removed extra Program/University separator sections.
- Kept compact paired controls for Degree/Language, City/University type,
  and Academic year/Intake.
- Improved Tuition layout without hiding currency.
- Reworked mobile filters into a full-width touch-friendly panel.
- Improved mobile checkbox grid and action buttons.
- Preserved all existing filter names and business logic.

### Programs mobile filter drawer
- Kept the accepted compact desktop filter layout.
- Gave Tuition two usable amount fields with a full-width currency selector.
- Polished checkbox states and Apply/Clear actions.
- Replaced the stacked mobile sidebar with a full-screen filter drawer.
- Added a mobile Filters trigger above results, close/backdrop/Escape behavior,
  scrollable filter content, and sticky Apply/Clear actions.
- All filters remain visible in the drawer; none are hidden as advanced options.

### Removable active program filters
- Removed the duplicate matching-program count from the Programs hero.
- Kept one result count above the catalogue.
- Added removable active-filter chips that preserve all other query parameters.
- Added one Clear all action for active filters.
- Removed the redundant sidebar Clear all action.
- Active chips scroll horizontally on mobile.

### Pagination current-tab navigation
- Pagination links no longer force a new browser tab.
- Previous, page-number and Next links now use normal same-tab navigation.
- Added regression coverage to prevent `target="_blank"`/`window.open()` from
  being introduced into the shared pagination template.

### Mobile catalogue containment fix
- Removed the closed Programs filter drawer completely from mobile document flow.
- Prevented the filter form from appearing between program cards or in stitched
  full-page screenshots.
- Forced the Programs results panel and cards to use the full mobile content width.
- Added the same one-column/mobile-width safeguards to shared public card grids
  used by university, program-detail, application and home-page lists.
- Added regression coverage for filter-drawer containment and mobile grid sizing.

### Global mobile shell correction
- Replaced the crowded desktop navigation on mobile with a compact logo + menu button.
- Added a touch-friendly mobile navigation menu shared by every public page.
- Tightened global mobile page spacing and ensured content uses the viewport width.
- Improved Programs cards, hero, active-filter chips and controls on narrow screens.
- Added explicit ultra-narrow safeguards for small phones.
- Moved Programs filter JavaScript out of the HTML title block into the page script block.
- Added regression tests for the mobile shell and template title safety.

### Mobile filter scrolling fix
- Made the Programs mobile filter drawer use a fixed `100dvh` viewport.
- Changed the drawer layout to a two-row grid: sticky header + scrollable form.
- Enabled independent touch scrolling with `overflow-y:auto`,
  `-webkit-overflow-scrolling:touch`, and `touch-action:pan-y`.
- Added bottom padding so the final filter controls are not hidden behind the
  sticky Apply action.
- Added regression coverage for mobile drawer scrolling.

### Tuition currency on programme cards
- Program cards now show tuition amounts together with their ISO currency code.
- The minimum tuition and currency are selected from the exact same active
  ProgramOffering, preventing mismatched amount/currency combinations.
- Offering-level filters also affect the displayed minimum tuition/currency.
- Updated Programs, University detail, and related-program cards.

### Currency display formatting
- Added central Django currency template filters.
- Programme/catalogue cards now use compact currency symbols (`$15,000`,
  `€12,500`, `₺8,500`).
- Detailed tuition/offerings use symbol + ISO code (`$15,000 USD`, etc.).
- Stored values and filter query parameters remain ISO currency codes.
- Unknown currencies safely fall back to their ISO code.

### Program tuition-currency test fixture fix
- Exposed the existing AcademicYear fixture as `self.year` in
  `ProgramFilterTests`.
- Fixed the regression test for matching minimum tuition and currency.

### Header navigation information architecture
- Separated public navigation from authenticated workspace/account actions.
- Moved Dashboard and Applicants into a workspace group on the utility side.
- Moved the language selector beside the account controls instead of the
  middle of the primary navigation.
- Replaced top-level Profile / Sign-in methods / Logout links with an account
  dropdown.
- Added icons for Profile, Sign-in methods and Logout.
- Added Sign-in methods as a permanent account-security card on Profile.
- Updated mobile navigation to mirror the same information hierarchy.

### Mobile homepage redesign
- Simplified the mobile hero around program/university search.
- Moved secondary hero filters to the full Programs catalogue on mobile.
- Converted Featured universities and application steps into swipeable rows.
- Capped study-field cards on the homepage and added a Browse all fields link.
- Made Popular programs substantially denser on phones.
- Compressed trust, FAQ, CTA and footer sections to reduce page length.
- Polished the hamburger menu as a compact mobile sheet.
- Kept the desktop homepage layout unchanged.

### Unified university cards
- Added one shared university-card template used by both Home and Universities.
- University catalogue cards now expose the same metadata as Featured universities.
- Added active program counts to the Universities queryset.
- Standardized type, YÖK, MOE, MOH, Erasmus, dormitory and program-count badges.
- Kept layout differences in CSS only: carousel-style on mobile Home, normal
  catalogue grid/list on the Universities page.
- Added regression tests to prevent the two card implementations from drifting.

### Fully clickable university cards
- Made the entire shared university card a single accessible link.
- Home Featured universities and the Universities catalogue now both open the
  university detail page when any part of the card is clicked.
- Removed nested card links to keep the HTML valid.
- Added keyboard focus styling and regression coverage.

### University detail program catalogue
- Rebuilt the university program catalogue using the main Programs catalogue UI.
- Shared the same program discovery card between both catalogue pages.
- Added removable active filters, Clear all, result summary and mobile drawer.
- Standardized tuition display and responsive behavior.

### University detail mobile experience
- Reworked the mobile university hero with a stronger name/logo hierarchy.
- Enlarged the university banner and separated identity from the program catalogue.
- Removed repeated university branding from program cards on university pages.
- Ensured the filter panel remains an off-canvas drawer and never consumes
  result width while closed.
- Added a compact mobile program count, larger filter trigger, comfortable
  full-width cards, larger typography and clearer pagination.
- Kept the shared Program card component for consistency with `/programs/`.

### Lead message attachment path fix
- Increased `LeadMessageAttachment.file` storage-path capacity to 500 characters.
- Added migration `0002_expand_message_attachment_file_path`.
- Stored message attachments now use a generated UUID filename while retaining
  the original extension.
- The user-facing original filename continues to be stored in `original_name`.
- Added regression tests for long filenames and bounded storage paths.

### Applicant workflow responsive forms
- Rebuilt Study preferences as grouped, mobile-first sections instead of `form.as_p`.
- Replaced huge checkbox lists for languages, cities, universities and fields
  with searchable multi-select controls and removable selected chips.
- Kept degree and university-type choices visible as compact checkbox groups.
- Added a shared sticky form action area and responsive applicant form grid.
- Improved applicant detail, interests, documents, messages and sidebar behavior
  on small screens.
- Added regression coverage for searchable selectors and mobile layout.

### Preference selector deduplication
- Deduplicated Study preference department choices by normalized English name.
- Existing duplicate department selections are mapped to the canonical choice
  when the form is edited.
- Reduced autocomplete results from 40 to 12 visible matches.
- Reduced the selector dropdown height on desktop and mobile.
- Added regression tests for duplicate and blank labels.

### Applicant mobile form test isolation fix
- Changed `ApplicantMobileFormTests` from `SimpleTestCase` to `TestCase`.
- `LeadPreferenceForm` now performs database-backed canonical department
  selection, so its regression test requires normal Django test database access.

### Searchable multi-select continuous selection
- Fixed searchable preference selectors closing after each selected item.
- The dropdown now stays open while the search input remains focused.
- Users can select multiple universities, cities, languages or fields in one
  continuous interaction without clicking outside and reopening the selector.
- Escape and outside-click behavior still close the dropdown.

### Searchable multi-select reopen behavior
- Restored close-after-selection behavior for searchable preference selectors.
- Fixed reopening when the search input remains focused after a selection.
- Clicking the search input now explicitly opens the option list, while focus
  also opens it for keyboard navigation.
- Escape and outside-click continue to close the selector normally.

### Agent operations workspace
- Added a dedicated agent dashboard at `/agent/`.
- Added agent-scoped applicant queue, applicant detail, message inbox and replies.
- Added program-request handling for customer catalogue applications.
- Added formal application queue/detail and status management.
- Added per-agent-user unread message handling.
- Added strict queryset-level tenant isolation through `Agent.users`.
- Added desktop/mobile Agent workspace navigation and responsive UI.
- Added regression tests for access isolation, read receipts and replies.
- Added `docs/agent-workspace.md`.

### Agent workspace test fixture fix
- Reused the `LeadConversation` automatically created by the Lead post-save signal in Agent Workspace tests.
- Removed the duplicate conversation creation that violated the one-to-one `LeadConversation.lead` constraint.

### Default lead agent setting
- Added singleton `LeadAssignmentSettings` with a configurable `default_agent`.
- Newly created leads automatically receive the active default agent when no
  explicit agent was supplied.
- Explicit lead-agent assignments are never overwritten.
- Added Django Admin management, migration, tests and agent-workspace docs.

### Default lead agent moved to environment setting
- Replaced the database-backed lead-assignment settings model with
  `settings.DEFAULT_LEAD_AGENT_ID`.
- Added `DEFAULT_LEAD_AGENT_ID` to `.env.example`.
- New leads use the configured active Agent UUID only when no explicit Agent is
  already set.
- Added a cleanup migration for the superseded database settings model.
- Updated tests and Agent Workspace documentation.

### Branded privacy-safe 404 pages
- Added a polished TurkDemy 404 page.
- Agent applicant/application detail views now render it directly for
  unavailable scoped resources, even during development.
- Error wording does not reveal whether a resource belongs to another agent.
- Added a global production `handler404` and regression tests.

### Consistent branded 404s in development
- Added HTML-only `BrandedNotFoundMiddleware`.
- Normal site 404s now use TurkDemy's branded page even with `DEBUG=True`.
- API, health and non-HTML 404 responses remain untouched.
- Real non-404 developer exceptions remain visible in development.
- Preserved specialized Agent Workspace 404 actions and privacy-safe wording.

### Fully clickable program cards
- Made the entire shared program discovery card clickable, matching university cards.
- Removed nested title/CTA anchors while preserving their visual affordances.
- Added keyboard focus styling and regression tests.

### Fully clickable similar-program cards
- Made every card in the program-detail "Similar programs" section clickable.
- Removed nested title and action anchors while preserving their visual affordances.
- Added keyboard focus styling and regression tests.

### Applicant form layout
- Rebuilt add/edit applicant as grouped responsive sections.
- Moved Save/Cancel actions to a stable footer after all fields.
- Added compact multi-column desktop layout and single-column mobile behavior.

### Explicit consumer email login-code routing
- Made the email sign-in button explicitly use `account_request_login_code`.
- Made request/confirm forms explicitly post to the login-code endpoints.
- Added regression tests ensuring login-code and signup routes remain separate.

### Branded outgoing email system
- Added a shared responsive TurkDemy HTML email template.
- Added branded HTML fallback for all django-allauth account emails.
- Updated the project email service to always send branded multipart mail.
- Added a dedicated sign-in-code email with a prominent code block.
- Changed login and email-verification codes to five numeric digits.
- Added regression tests and email documentation.

### Superuser Email Preview Gallery
- Added `/admin-tools/email-previews/` for superusers only.
- Registered every django-allauth account email type with safe sample data.
- Added previews for every configured TurkDemy language.
- Added HTML/plain-text inspection and "Send test to myself".
- Added missing-translation warning for previews identical to English.
- Added a Django system check that fails when allauth introduces an outgoing
  email that has not been registered in the gallery.
- Project email sends now require a registered `email_type`.

### Reliable email preview bodies
- Replaced `iframe srcdoc` with a dedicated superuser-only HTML preview endpoint.
- Added validation for non-empty subject, plain-text and HTML email bodies.
- Added explicit preview rendering errors instead of blank frames.
- Added regression coverage for every registered email type in every supported language.

### Localized email brand display name
- Added a translatable `TurkDemy` brand display name for outgoing email.
- Persian email now uses `ترک‌دمی`; Arabic uses `ترك ديمي`.
- English and Turkish keep `TurkDemy`.
- Shared branded emails and allauth-generated account emails now use the localized display name.
- Domains remain canonical and untranslated.
- Added regression tests and documentation.

### Explicit application status
- Added `applied` to `LeadProgramInterestStatus`.
- Program Apply actions now create/promote interests to `applied`.
- Applicant detail distinguishes applications, interests and recommendations.
- Applied programs show their intake or "Any intake / decide later".
- Success messaging now says "Application started for <program>".

### Simplified applicant program associations
- Reduced program provenance to `user` and `agent` only.
- Removed system-generated program suggestions.
- Removed the interest-status lifecycle (interested/shortlisted/applied/etc.).
- Applicant UI now shows a simple Programs list with "Added by you" or
  "Suggested by your advisor".
- Agent UI no longer exposes program-request status controls.
- Lead-to-Student conversion no longer auto-creates formal Applications from
  the collaborative program list.
- Existing `system` source rows are migrated to `agent`.

### Agent document review and chat promotion
- Added pending/approved/rejected review states for applicant documents.
- Added reviewer, review timestamp and review note.
- Added Open + Review controls to Agent Workspace.
- Added "Add to documents" for customer chat attachments.
- Chat files are copied to LeadDocument storage and linked back to their source attachment.
- Prevented duplicate attachment promotion.
- Updated the Agent Workspace Programs panel to user-added / agent-suggested provenance.

### Document replacement lifecycle
- Renamed document "Rejected" to "Replacement requested".
- Added customer-visible replacement reason and Replace document action.
- Added review-history audit records.
- Added archived document versions before replacement.
- Replacement updates the existing document and resets it to pending review.
- Replacement requests and replacement uploads generate conversation messages.

### Customer document upload modal
- Replaced the large inline customer upload form with a compact modal.
- Removed the customer-facing document name input.
- Document name is derived automatically from the uploaded filename.
- Reduced Description to a compact optional textarea.

### Simplified lead lifecycle
- Lead statuses are now New, Assigned, Finalized, and Closed.
- Assignment to an agent user automatically drives New/Assigned status.
- All users of the assigned Agent retain visibility; `assigned_to` is responsibility only.
- Added Assign to me/reassignment in Agent Workspace.
- Added close/reopen workflow with close audit metadata.
- Finalized now specifically means converted to Student; validation is no longer a status.
- Agent list/detail show the responsible agent user.

### Agent responsibility controls
- Agent Workspace now shows the responsible user's full name and `(You)` for
  the current user.
- Added Assign agent / Reassign modal restricted to active users of the Lead's
  Agent.
- Kept Assign to me as the fastest takeover action.
- Clarified that assignment controls responsibility, not lead visibility.
- Replaced the small Close applicant disclosure with a proper modal action.

### ChatGPT SDD agent contract
- Strengthened the root `AGENTS.md` as the standing contract for ChatGPT/coding agents.
- Defined explicit source-of-truth precedence for domain rules, ADRs, specs, design, tasks, tests, code, and UI/legacy docs.
- Added one-request implementation semantics so clear user requests can drive the full spec-to-code cycle without unnecessary separate approval turns.
- Added requirement-to-test/UI verification expectations and repository documentation duties.
- Added a delivery contract requiring the complete updated project archive after repository changes and truthful reporting of executed checks.
- Linked the human-facing SDD workflow to the agent contract and documented full-cycle execution in `docs/SDD.md`.

## 2026-08-28 — SDD Foundation v2

- Added executable `tools/sdd/check.py` validation and `make sdd-check`.
- Wired SDD validation into `make check`.
- Upgraded active capability traceability to requirement-level rows while preserving explicit verified mappings where present.
- Ensured every active capability has the four SDD artifacts, including baseline task files for communication-log and todo-management.
- Added `docs/domain/invariants.md` and `docs/domain/lifecycle-map.md` without inventing unspecified transitions.
- Added regression tests for the SDD contract.
