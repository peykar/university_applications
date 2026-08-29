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

## JSON schema version 1

The file root is an object with:

- `schema_version`: required integer, currently `1`.
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

`academic_unit` and `department` are either `null` or the `slug_en` of an item
defined in the corresponding top-level array.

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
  "semester": "Fall",
  "fee_basis": "annual",
  "currency": "USD",
  "tuition": "30000.00",
  "tuition_discount_percentage": null,
  "tuition_discounted": "25000.00",
  "cash_discount_percentage": null,
  "tuition_cash": "23000.00",
  "tuition_annual_installment": null,
  "deposit": "1000.00",
  "preparatory_tuition": null,
  "preparation_included": false,
  "quota": null,
  "deadline": null,
  "valid_from": null,
  "valid_until": null,
  "notes": "Source terminology or footnotes can be preserved here.",
  "is_active": true
}
```

Allowed `fee_basis`: `annual`, `whole_program`.

Allowed `currency`: `USD`, `EUR`, `TRY`.

Money and percentage values should be JSON strings so the source decimal value
is preserved exactly. `tuition` is required. Optional monetary fields may be
`null`. Date values use ISO `YYYY-MM-DD` or `null`.

An Offering is upserted by the tuple:

```text
Program + AcademicYear + Semester + UniversityCatalogueSource
```

The `UniversityCatalogueSource` comes only from the command argument, so every
offering imported by one command run has explicit provenance. If more than one
existing Offering already matches that key, the command stops rather than
choosing one silently.

Academic years and semesters are looked up by `name_en` and created when they do
not already exist.

## Update and safety rules

- Programs, AcademicUnits and Departments are updated by stable English slug.
- Offerings are updated by Program + AcademicYear + Semester + source.
- Re-running the same file is idempotent for those import keys.
- Rows absent from a later JSON file are not deleted or deactivated.
- The command never infers missing tuition semantics, percentages, study mode,
  validity, or other ambiguous values.
- The complete import runs in one database transaction.
