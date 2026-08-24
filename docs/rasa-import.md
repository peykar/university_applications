# RasaStudy Import Commands

TurkDemy can import the files produced by `scripts/download_rasastudy.py`.

## Recommended flow

Download:

```bash
make rasa-download
```

Populate ISO countries first:

```bash
uv run python manage.py populate_countries
```

Import everything:

```bash
make rasa-import
```

Equivalent command:

```bash
uv run python manage.py import_rasa_data data/rasa
```

## Catalogue only

```bash
uv run python manage.py import_rasa_catalogue data/rasa
```

Optional intake mapping:

```bash
uv run python manage.py import_rasa_catalogue data/rasa \
  --academic-year 2026-2027 \
  --semester Fall
```

The importer maps Rasa's flattened pricing/intake values into
`ProgramOffering`.

### Important mapping

Rasa:

```text
University
Program
  tuition_usd
  tuition_discounted_usd
  tuition_cash_usd
  tuition_annual_installment_usd
  quota
  deadline
```

TurkDemy:

```text
University
Program
└── ProgramOffering
    ├── tuition
    ├── tuition_discounted
    ├── tuition_cash
    ├── tuition_annual_installment
    ├── quota
    └── deadline
```

`boost_score` is mapped to `listing_priority`.

Rasa university flags:

```text
moe_approved
moh_approved
erasmus
has_dorm
```

map to TurkDemy university fields.

## FAQ/content only

```bash
uv run python manage.py import_rasa_content data/rasa
```

Supported FAQ-category container keys:

```text
cats
categories
faq_categories
```

Supported FAQ container keys:

```text
faqs
faq
```

## Idempotency

The commands use `update_or_create()` so rerunning an import updates existing
records instead of intentionally duplicating them.

## Geography caveat

Rasa provides city text but not a complete province hierarchy. The catalogue
importer creates a minimal province/city structure using the Rasa city name
for both levels. This is an import fallback and can later be replaced with a
proper Turkish province/city dataset.

## Mapping reference

See `docs/rasa-mapping.md` for the canonical source-to-model mapping, including media handling.

## Audit actor

Rasa imports use the `.env`-configured system user. New imported rows receive
both `created_by` and `updated_by`; re-imported rows preserve `created_by` and
set `updated_by` to the system user. See `docs/auditing.md`.
