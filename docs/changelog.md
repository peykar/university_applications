# Changelog

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
