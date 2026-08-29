# FEAT-0008 — Program internal notes

Status: IMPLEMENTED / LOCAL VERIFICATION REQUIRED
Date: 2026-08-30

## Request

Provide a Program-level field for import/provenance commentary that must not be
shown to end users. This prevents operational normalization notes from being
placed in localized customer-facing descriptions.

## Requirements

- `CAT-031`
- Consistent with `BR-AUD-002` (internal notes are Agent/staff-only).

## Implementation

- Added optional `Program.internal_notes` text storage.
- Added the field to a collapsed staff-only Program admin section.
- Extended schema-v1 `import_programs_for_university` JSON with optional
  `internal_notes`; re-import updates the value under the existing Program key.
- Kept `internal_notes` out of public/customer templates and the public Program
  API serializer.

## Migration

This repository's delivery archives do not contain generated application
migrations. After applying this change to a development checkout, generate and
apply the local migration before running the full suite:

```bash
uv run --env-file .env python manage.py makemigrations universities
uv run --env-file .env python manage.py migrate
```

## Verification

Regression coverage was added for JSON create/update behavior and for absence
from public/customer templates and the public Program serializer. Run
`make format` and `make check` in the project environment after migration.
