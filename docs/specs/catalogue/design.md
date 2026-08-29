# University and program catalogue — technical design

Status: APPROVED
Version: 2.0

## Domain shape

```text
University
 ├── AcademicUnit*
 │    └── type
 ├── Department*
 ├── UniversityCatalogueSource*
 └── Program*
      ├── AcademicUnit? -> same University
      ├── Department?   -> same University
      ├── study_mode
      ├── duration (unambiguous/fraction-safe)
      ├── ProgramInstructionLanguage*
      │    ├── ProgramLanguage
      │    ├── percentage?
      │    └── is_primary
      └── ProgramOffering*
           ├── AcademicYear
           ├── Semester
           ├── fee_basis / currency
           ├── tuition
           ├── tuition_discounted
           ├── tuition_cash
           ├── deposit
           ├── preparatory_tuition
           ├── preparation_included
           ├── quota / deadline
           ├── valid_from / valid_until
           ├── notes
           └── source? -> UniversityCatalogueSource
```

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

The legacy `program_language` field is a migration bridge only: populate the
through table first, update all readers/importers, then remove the legacy field
in a later migration after compatibility tests pass.

### Study mode

Add a Program choice field with stable values `on_campus`, `distance`, `online`,
`hybrid`. Default existing rows to `on_campus`; importers may override only from
source evidence.

### Duration

Use a fraction-safe canonical representation. Preferred implementation is
`duration_months` as a positive integer because it is unambiguous and supports
1.5-year programmes exactly. Migration must explicitly translate the current
legacy duration according to its documented/current unit. If investigation
shows legacy duration is not consistently years, stop migration and record a
CONFLICT rather than guessing.

### UniversityCatalogueSource

Add a University-owned source record containing title, optional uploaded file,
received date, optional AcademicYear, optional valid-from/until, source notes,
and recorded-by User. Source records are provenance and must not be cascade-
deleted merely because an Offering changes. Prefer protective/null-safe
relations according to existing file-retention conventions.

### ProgramOffering

Retain the existing offering as the intake/commercial boundary. Do not move
pricing onto Program. Keep existing numeric pricing fields and formally define
their semantics in the spec. Rename `pre_school_fees` to
`preparatory_tuition` with a data-preserving migration. Add
`preparation_included`, `notes`, `valid_from`, `valid_until`, and optional
`source`.

Do not add a generic OfferingPrice table in v2. Current source samples are
covered by standard, discounted/offered, cash/advance, deposit, and preparatory
amounts; over-normalising now would add complexity without an approved need.

## Admin/agent maintenance

Program editing must group stable academic identity separately from offering
commercial data. Offering maintenance exposes all CAT-019 fields. Source is
selectable only from the same University as the Program/Offering.

AcademicUnit, Department, language composition, study mode and duration are
Program-level inputs. Agent-facing validation must explain invalid mixed
language percentages and cross-University selections.

## Import and migration strategy

Implement in compatibility stages:

1. Add new nullable/compatible structures and source model.
2. Backfill one ProgramInstructionLanguage from each legacy single language.
3. Backfill canonical duration without changing displayed meaning.
4. Rename/copy preparatory fee data without loss.
5. Update Rasa import and admin/read paths to write/read canonical structures.
6. Update public filters/detail pages and admissions selectors.
7. Remove/deprecate legacy language/duration paths only after regression tests
   prove no remaining readers/writers.

University-supplied sheets are evidence, not automatically trusted normalized
input. Import code must not infer percentages, study mode, validity, or pricing
semantics where the source is ambiguous; preserve the raw/source note instead.

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
- No admission workflow semantics change as part of catalogue v2.
- Preserve i18n/RTL behavior and existing localized catalogue naming patterns.

## Architecture decision

See `docs/architecture/decisions/ADR-006-university-catalogue-v2.md`.
