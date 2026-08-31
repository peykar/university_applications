# University catalogue data dump

Use `dump_university_data` to export one University's catalogue-domain data to a
versioned UTF-8 JSON file. This is intended for offline comparison, Rasa text
matching, translation enrichment, and catalogue audits. It is not a full database
backup.

## Usage

```bash
uv run --env-file .env python manage.py dump_university_data <UNIVERSITY_ID>
```

By default this writes:

```text
university_<UNIVERSITY_ID>_catalogue.json
```

To choose a destination:

```bash
uv run --env-file .env python manage.py dump_university_data \
  <UNIVERSITY_ID> \
  --output data/turkdemy/rasa/medipol.json
```

The University ID is the command's only required input.

## Export scope

Schema version 2 exports the University and its catalogue relationships:

- localized University names, slugs, descriptions, flags, rankings and location;
- nested City, Province and Country localized values;
- UniversityMedia metadata (stored image name, title, ordering, active state);
- AcademicUnits and Departments with localized names/slugs/descriptions;
- UniversityCatalogueSources and their academic-year/validity/source notes;
- Programs with localized names/slugs/descriptions, `internal_notes`, academic
  structure, degree, thesis type, study mode, canonical duration;
- canonical ProgramInstructionLanguage rows and referenced localized language;
- ProgramOfferings with academic year/intake, structured fees, quota/deadline, validity,
  notes and catalogue-source reference. Catalogue v2 compatibility fields are not exported.

The command intentionally does **not** export Leads, Students, Applications,
messages/conversations, customer accounts, or other admissions/customer data.
File and image binaries are not embedded; stored file names are exported instead.
Decimals are strings so exact monetary values are preserved.

## Rasa enrichment workflow

Dump the Rasa-created University, provide the resulting JSON as the text source,
and match it only against the official-import University for the same institution.
The Rasa dump can then supply existing localized `name_*` and `description_*`
content without treating its older tuition/offering values as authoritative.
