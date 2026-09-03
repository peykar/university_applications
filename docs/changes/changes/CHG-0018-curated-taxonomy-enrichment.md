# CHG-0018 — Curated taxonomy and City SEO enrichment

Status: VERIFYING
Requested: 2026-09-03

## Request

Use the exported current TurkDemy catalogue to prepare a one-time, reviewable data
enrichment operation: create the GeneralField taxonomy, map active Programs to one
or more fields, and enrich used City records with multilingual editorial/SEO data.

## Classification

CHANGE

## Affected requirements

- `CAT-053`–`CAT-058` — GeneralField taxonomy and manual-curation boundary.
- `CAT-059` — City editorial/SEO metadata.
- `CAT-060` — one-time curated enrichment operation.

## Source snapshot

The supplied export contains 5,509 active Programs, 8 active Universities, and one
used City (`istanbul`). The curated mapping pins assignments to Program UUIDs from
that snapshot. 5,508 active Programs receive one or more GeneralFields. One malformed
record (`b16d8718-7e8a-46d8-bb68-50913baad85e`, English name `biruni`) is deliberately
left unmapped and reported for manual review.

## Desired behavior

- Keep university-owned AcademicUnit/Department data unchanged.
- Seed/update 24 multilingual GeneralFields with editorial and SEO metadata.
- Add (never infer during normal imports) one or more curated GeneralFields to the
  5,508 reviewed active Program UUIDs.
- Preserve any pre-existing Program-GeneralField links.
- Enrich the existing Istanbul City row by `slug_en`; never create a duplicate City.
- Support `--dry-run` with a full transaction rollback.
- Report missing/inactive mapped UUIDs and the deliberately withheld malformed row.

## Verification

- [x] Python syntax/compile validation in delivery environment.
- [x] SDD traceability updated.
- [ ] `make format` locally.
- [ ] `make check` locally.
- [ ] `uv run --env-file .env python manage.py makemigrations geography`.
- [ ] `uv run --env-file .env python manage.py migrate`.
- [ ] `uv run --env-file .env python manage.py enrich_taxonomy --dry-run` reviewed.
- [ ] `uv run --env-file .env python manage.py enrich_taxonomy` applied once approved.
