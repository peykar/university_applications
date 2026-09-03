# University programme JSON import

TurkDemy can import a normalized programme catalogue for one existing University
and one existing `UniversityCatalogueSource` with:

```bash
uv run --env-file .env python manage.py import_programs_for_university \
  <university-id> \
  <university-catalogue-source-id> \
  path/to/programs.json
```

The source must belong to the supplied University. The command is atomic: an
invalid file or import error rolls back the whole import.

## Program slug collisions

Program public slugs are generated from structured catalogue data. If two Programs resolve
to the same localized canonical slug during an import, the first persisted owner keeps the
base and later owners receive the smallest available numeric tail (`-2`, `-3`, ...). Valid
existing tails are preserved on re-import. Use `rebuild_program_slugs` when a global,
Program-ID-deterministic normalization of base/tail ownership is required.

## JSON schema version 2

The file root is an object with:

- `schema_version`: required integer, currently `2`.
- `academic_units`: optional array. Each row is upserted inside the supplied
  University by `slug_en`.
- `departments`: optional array. Each row is upserted inside the supplied
  University by `slug_en`.
- `programs`: required non-empty array. Each Program is upserted inside the
  supplied University by `slug_en`.

The file does not identify its University or catalogue source because those are
explicit command arguments. It also does not delete database rows that are
absent from the file.

### Academic unit

```json
{
  "slug_en": "faculty-of-medicine",
  "name_en": "Faculty of Medicine",
  "name_fa": "",
  "name_tr": "",
  "name_ar": "",
  "slug_fa": "",
  "slug_tr": "",
  "slug_ar": "",
  "unit_type": "faculty",
  "description_en": "",
  "description_fa": "",
  "description_tr": "",
  "description_ar": "",
  "is_active": true
}
```

Allowed `unit_type` values are:
`faculty`, `school`, `institute`, `vocational_school`, `conservatory`,
`college`, `graduate_school`, `other`.

### Department

Departments use the same localized name/slug and description fields but do not
have `unit_type`.

### Program

```json
{
  "slug_en": "medicine-english",
  "name_en": "Medicine",
  "name_fa": "",
  "name_tr": "",
  "name_ar": "",
  "slug_fa": "",
  "slug_tr": "",
  "slug_ar": "",
  "description_en": "",
  "description_fa": "",
  "description_tr": "",
  "description_ar": "",
  "internal_notes": "Internal normalization/provenance note; never customer-facing.",
  "degree": "bachelor",
  "thesis_type": null,
  "academic_unit": "faculty-of-medicine",
  "department": null,
  "study_mode": "on_campus",
  "duration_months": 72,
  "listing_priority": 0,
  "is_active": true,
  "instruction_languages": [
    {
      "slug": "english",
      "name_en": "English",
      "percentage": "100",
      "is_primary": true
    }
  ],
  "offerings": []
}
```

Allowed `degree` values: `associate`, `bachelor`, `master`, `phd`.

Allowed `thesis_type` values: `thesis`, `non_thesis`, or `null`.

Allowed `study_mode` values: `on_campus`, `distance`, `online`, `hybrid`.

`duration_months` is a positive integer or `null`. Fractional-year programmes
are represented exactly in months, for example 18 months for 1.5 years.

`internal_notes` is optional staff/import-only text. Use it for normalization
decisions, source interpretation, matching remarks, or other operational context
that must not appear in customer-facing programme descriptions. It is imported
onto `Program.internal_notes` and is intentionally excluded from public/customer
templates and the public Program API serializer. If the key is omitted on a
re-import, the existing internal note is preserved; use an empty string or `null`
when the import should explicitly clear it.

`academic_unit` and `department` are either `null` or the `slug_en` of an item
defined in the corresponding top-level array.

`general_field` and `general_fields` are deliberately **not** part of the normalized import contract.
GeneralField is TurkDemy-curated after catalogue verification. A new imported
Program therefore has no GeneralField assignments, while re-importing an existing
Program preserves all GeneralFields already assigned manually. Supplying either a
`general_field` or `general_fields` key in a Program import row is rejected before writes.

Every Program must contain at least one instruction language. Language entries
are matched globally by `slug`; a missing language vocabulary row is created
from `name_en` and optional localized name/slug fields. A file may mark at most
one primary language. If percentages are provided, every language must have a
percentage and the total must equal exactly 100. If the source does not provide
percentages, all percentages must be `null`/omitted.

For Programs present in the file, the instruction-language list is authoritative
and replaces the Program's previous through-table composition. Other Programs
are untouched.

### Offering

```json
{
  "academic_year": "2026-2027",
  "intake": "Fall",
  "fees": [
    {"fee_type": "tuition", "currency": "USD", "amount": "30000.00", "basis": "annual"},
    {"fee_type": "discounted_tuition", "currency": "USD", "amount": "25000.00", "basis": "annual"},
    {"fee_type": "deposit", "currency": "USD", "amount": "1000.00", "basis": "one_time"}
  ],
  "preparation_included": false,
  "quota": null,
  "deadline": null,
  "valid_from": null,
  "valid_until": null,
  "notes": "Source terminology or footnotes can be preserved here.",
  "is_active": true
}
```

`intake` is required. `fees` is a required array and may be empty when pricing is
unknown. Each fee explicitly supplies `fee_type`, `currency`, and `basis`, plus at
least one of `amount` or `percentage`. Supported fee types are `tuition`,
`discounted_tuition`, `advance_payment`, `cash_payment`, `installment_total`,
`deposit`, `preparatory`, `application`, `registration`, and `other`. Supported
bases are `annual`, `semester`, `whole_program`, `per_credit`, and `one_time`.

An Offering is upserted by Program + AcademicYear + Intake +
UniversityCatalogueSource. Catalogue v2 `semester` and fixed pricing fields are
not part of schema version 2.

## Update and safety rules

- Programs, AcademicUnits and Departments are updated by stable English slug.
- Offerings are updated by Program + AcademicYear + Intake + source.
- Re-running the same file is idempotent for those import keys.
- Rows absent from a later JSON file are not deleted or deactivated.
- The command never infers missing tuition semantics, percentages, study mode,
  validity, or other ambiguous values.
- The command never assigns, overwrites, or clears TurkDemy's curated
  `Program.general_fields` classification.
- The complete import runs in one database transaction.
### Localized slug policy

`slug_en` is the deterministic import key and remains ASCII-only. `slug_fa`,
`slug_tr`, and `slug_ar` may use valid native Unicode slug characters, including
Persian, Turkish, and Arabic letters, plus numbers, underscores, and hyphens.
They do not need to be transliterated or copied from `slug_en`. The importer runs
normal Django model validation, so spaces and other non-slug punctuation remain
invalid.

## Program public slug canonicalization

The JSON `programs[].slug_en` remains the source-native/program-only import key
(e.g. `nursing-bachelor-turkish`). TurkDemy persists Program public slugs in the
canonical globally unique form `<university-slug>-<program-slug>`. Re-imports
match both the legacy program-only key and canonical key during the transition.
Localized Program slugs are likewise prefixed with the corresponding localized
University slug when that University slug is available.

For existing databases, see `docs/program-slug-rebuild.md`.
