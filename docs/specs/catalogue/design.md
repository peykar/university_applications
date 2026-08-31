# University and program catalogue — technical design

Status: APPROVED
Version: 3.2

## Domain shape

```text
University
 ├── AcademicUnit*
 ├── Department*
 ├── UniversityCatalogueSource*
 └── Program*
      ├── AcademicUnit? / Department?
      ├── study_mode / duration_months / internal_notes
      ├── ProgramInstructionLanguage* → ProgramLanguage
      └── ProgramOffering*
           ├── AcademicYear
           ├── Intake
           ├── OfferingFee*
           ├── preparation_included
           ├── quota / deadline / validity
           ├── notes
           └── source? → UniversityCatalogueSource
```

Catalogue v3 is the sole active persistence representation.

## Model design

### AcademicUnit

Add `AcademicUnit` under `apps.universities` with University ownership,
localized name fields consistent with existing catalogue entities, unit type,
active state, and normal audit/base-model fields where applicable. Enforce same
University when attached to Program.

### Instruction languages

Replace Program's single-language domain contract with a through model
`ProgramInstructionLanguage`. Keep `ProgramLanguage` as the canonical language
vocabulary. The through model stores `percentage` (nullable) and `is_primary`.
Use a database/service uniqueness invariant for `(program, language)`.

Percentage-total validation belongs in model/service/form validation because a
row cannot validate the aggregate alone. Null means "source did not state the
share", not zero.

The earlier single-language compatibility field has been removed. All language
readers and writers use `ProgramInstructionLanguage`.

### Program internal notes

Add an optional `Program.internal_notes` text field for provenance, normalization,
and staff/import commentary that does not belong in customer-facing programme
descriptions. The Django admin may expose it to staff, but public/customer
templates and the public Program API serializer must not expose it. The
normalized JSON importer accepts optional `internal_notes` and treats it as an
updatable Program attribute under the existing Program upsert key. This is
distinct from `ProgramOffering.notes`, which remains source/commercial context
for an Offering and may have its own presentation semantics.

### Study mode

Add a Program choice field with stable values `on_campus`, `distance`, `online`,
`hybrid`. Default existing rows to `on_campus`; importers may override only from
source evidence.

### Duration

Use `duration_months` as the sole stored duration. It is unambiguous and supports
fractional-year programmes such as 18 months without loss.

### UniversityCatalogueSource

Add a University-owned source record containing title, optional uploaded file,
received date, optional AcademicYear, optional valid-from/until, source notes,
and recorded-by User. Source records are provenance and must not be cascade-
deleted merely because an Offering changes. Prefer protective/null-safe
relations according to existing file-retention conventions.

### ProgramOffering

`ProgramOffering` is the intake/availability/provenance boundary. It stores the
canonical `Intake`, academic year, preparation-inclusion flag, quota/deadline,
validity, notes, and source. Monetary values are not columns on ProgramOffering.
Each price/percentage is an `OfferingFee` with explicit fee type, currency, basis,
optional language, label, and notes.

## Admin/agent maintenance

Program editing must group stable academic identity separately from offering
commercial data. Offering maintenance exposes all CAT-019 fields. Source is
selectable only from the same University as the Program/Offering.

AcademicUnit, Department, language composition, study mode and duration are
Program-level inputs. Agent-facing validation must explain invalid mixed
language percentages and cross-University selections.

## Import and transition strategy

The compatibility transition is complete. New code must not create or read the
removed Semester, single-language Program field, whole-year duration field, or
fixed ProgramOffering price columns. Source ambiguity is preserved in notes rather
than guessed.

### Normalized per-University JSON import

`import_programs_for_university` accepts University UUID,
UniversityCatalogueSource UUID, and a schema-v2 JSON path. Programs use `slug_en`
as their deterministic key. Offerings use Program + AcademicYear + Intake + source.
Instruction-language rows are authoritative for imported Programs, and each
Offering carries a structured `fees` array. The whole import is atomic.

### Rasa import

Rasa source columns are normalized directly into `duration_months`,
`ProgramInstructionLanguage`, university/year-specific `Intake`, and `OfferingFee`
rows. The `--semester` command-line spelling is accepted only as an alias for
`--intake`; it does not create a Semester model or compatibility data.

## Public catalogue

Language filters match any canonical instruction-language association. Mixed
language display renders known percentages where available. Study mode and
AcademicUnit become available presentation/filter dimensions where UX chooses
to expose them. Tuition filters continue to constrain a coherent Offering row.

## Cross-cutting constraints

- Follow `docs/product/business-rules.md` and terminology.
- Preserve existing LeadProgramInterest/Application relationships to Program and
  ProgramOffering.
- Existing Applications must retain valid Offering references through migrations.
- Admission workflow semantics remain unchanged except that Application pricing snapshots now read canonical structured OfferingFee data.
- Preserve i18n/RTL behavior and existing localized catalogue naming patterns.

## Architecture decision

See `docs/architecture/decisions/ADR-006-university-catalogue-v2.md`.

## University catalogue JSON dump

`dump_university_data <university-id>` produces a schema-v2 UTF-8 JSON snapshot
for offline catalogue comparison and text enrichment. The command accepts one
required positional argument; `--output` is an optional destination override.
The default filename is `university_<uuid>_catalogue.json`.

The export is deliberately catalogue-scoped rather than a database backup. It
contains localized University/geography data, media metadata, AcademicUnits,
Departments, catalogue sources, Programs (including internal notes), canonical
instruction languages, and ProgramOfferings. It does not traverse Leads,
Students, Applications, conversations, users, or other customer operational
records. File/image fields are represented by their stored names rather than
embedding binary content. Decimal values are emitted as strings to preserve
precision and dates use ISO-8601 strings.
## Localized Unicode slugs

The shared `LocalizedSlugMixin` keeps `slug_en` as Django's default ASCII-only
`SlugField` and enables `allow_unicode=True` only for `slug_fa`, `slug_tr`, and
`slug_ar`. Because University, AcademicUnit, Department, ProgramLanguage, Program,
and Country/Province/City share this mixin, model/admin/import validation now
uses the same native-script policy everywhere. This is a validation/state change;
it does not rewrite existing stored slugs.

Public, application, and API detail routes already use the single-segment
`<str:slug>` converter so persisted Unicode slugs can be reversed and resolved.
The normalized university-program JSON importer continues to use `slug_en` as its
deterministic upsert key, while localized slug fields may carry native Persian,
Turkish, or Arabic slugs. No transliteration or fallback to English is required.



## Automatic localized slug generation

Supported slug fields are optional input in admin forms. `BaseModel` inspects
`SlugField`s and fills only missing values where the related name mapping is known.
Localized `slug_<locale>` fields map to `name_<locale>`; conventional `slug` maps
to `name`; and the existing `FAQCategory.key` maps to `name_en`. English uses
Django `slugify(..., allow_unicode=False)` while Persian, Turkish, and Arabic
localized fields use their field-level Unicode setting.

Generation is fill-only: a non-empty slug is stable and is not regenerated when
its name later changes. This avoids unexpected public URL changes. A localized
name that is empty does not create a slug. `slug_en` remains the canonical ASCII
identifier/import key; this automation primarily removes manual admin work and
does not change normalized JSON import key semantics.

## Catalogue v3 transition completion

Catalogue v3 is now the sole active persistence model. `Program` stores canonical
`duration_months` and instruction-language through rows only. `ProgramOffering`
stores its `Intake`, availability/provenance metadata, and preparation-inclusion
flag; all monetary values, currencies, percentages and fee bases live in
`OfferingFee`.

Application creation is an explicit v3 consumer. It selects the same canonical
payable tuition used for presentation (discounted tuition first, then list
tuition), rejects offerings without an amount-bearing active tuition fee, and
snapshots an active structured deposit when one exists.

Normalized JSON import schema version 2 requires `intake` and a structured
`fees` array. Rasa source columns are translated directly into OfferingFee rows.
No importer writes a compatibility copy. Export and Admin likewise expose only
the canonical model.
