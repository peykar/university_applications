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
