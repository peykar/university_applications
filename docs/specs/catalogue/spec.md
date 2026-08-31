# University and program catalogue

Status: APPROVED
Version: 3.1

## Goal

Model university-supplied programme catalogues and agent tuition sheets without
flattening stable academic identity, intake-specific commercial terms, or source
provenance. The catalogue must support the structures observed in university
price lists while remaining suitable for public discovery and admissions.

## Requirements

CAT-001 — A Program MUST belong to one University.

CAT-002 — A Program Department, when present, MUST belong to the same University.

CAT-003 — ProgramOffering MUST hold intake-specific academic year, canonical Intake,
structured fee data and applicable quota/deadline data.

CAT-004 — University recognition/approval flags MUST remain on University and
MUST NOT be duplicated onto Program.

CAT-005 — Listing priority MUST be treated as internal ordering input and MUST
NOT be presented as academic quality/rank/sponsorship.

CAT-006 — Public catalogue filtering MAY use country, city, university, degree,
tuition, language and field/discipline dimensions supported by the data model.

CAT-007 — A University MAY define AcademicUnits. An AcademicUnit MUST belong to
one University and MUST classify its unit type as Faculty, School, Institute,
Vocational School, Conservatory, College, Graduate School, or Other.

CAT-008 — A Program MAY belong to one AcademicUnit. When present, the AcademicUnit
MUST belong to the Program's University. Department remains optional and is not
synonymous with AcademicUnit.

CAT-009 — A Program MUST support one or more instruction languages. Each language
association MAY record a percentage and MAY identify the primary language. Mixed
language programmes MUST NOT be represented by synthetic language names such as
"English & Turkish".

CAT-010 — When instruction-language percentages are supplied, each percentage
MUST be between 0 and 100 and the populated percentages for a Program MUST total
100. Unknown percentages MAY remain null.

CAT-011 — A Program MUST have a structured study mode supporting at least On
campus, Distance learning, Online, and Hybrid. Existing programmes default to On
campus unless imported evidence says otherwise.

CAT-012 — Program duration MUST support fractional-year source values without
loss. The canonical stored duration MUST have explicit units or an equivalent
unambiguous representation; public/admin display MAY render friendly years or
months.

CAT-013 — ProgramOffering pricing semantics MUST distinguish standard/list
tuition, offered/discounted tuition, cash/advance-payment tuition, and required
deposit. These values MUST NOT be treated as interchangeable.

CAT-014 — The existing preschool-like fee concept MUST be renamed/reframed as
preparatory tuition. Preparatory tuition refers to language/foundation
preparation, not childhood preschool education.

CAT-015 — A ProgramOffering MUST be able to state whether its quoted fee includes
preparatory study and MUST support free-text commercial/academic notes for
footnotes or exceptional charges that cannot be represented safely by numeric
fields alone.

CAT-016 — TurkDemy MUST preserve provenance for university-supplied catalogue
information through a UniversityCatalogueSource associated with one University.
A source MUST support a title/file reference, received date, optional academic
year, optional validity metadata, notes, and the Agent user who recorded it when
applicable.

CAT-017 — A ProgramOffering MAY reference the UniversityCatalogueSource from
which its intake/pricing data was derived. Source replacement MUST NOT silently
destroy historical provenance.

CAT-018 — Intake/pricing validity MUST support `valid_from` and `valid_until`
when supplied. Validity dates describe commercial/source validity and are
separate from academic year, intake, and application deadline.

CAT-019 — ProgramOffering admin/agent maintenance MUST expose the structured
commercial fields required by university sheets: academic year, intake, fee
basis, currency, standard tuition, offered/discounted tuition, cash/advance
payment tuition, deposit, preparatory tuition, quota, deadline, preparation
inclusion, validity, notes, and source.

CAT-020 — Program maintenance MUST expose University, AcademicUnit, optional
Department, degree, thesis type, study mode, duration, and instruction-language
composition without requiring agents to encode these dimensions in the Program
name.

CAT-021 — Existing catalogue/import data MUST be migrated without dropping the
current language, duration, tuition, or preparatory-fee information. Legacy
single-language data becomes one instruction-language association; legacy
integer duration MUST retain its current meaning during migration.

CAT-022 — Rasa/university importers MUST map source values into the new structured
fields when the source provides them and MUST preserve unsupported/unmapped
source information rather than inventing values.

CAT-023 — Public programme pages and filters MUST consume the canonical
multi-language, study-mode, duration, AcademicUnit, and offering-pricing data
once migrated. User-visible labels MUST not expose deprecated field semantics.

CAT-024 — Admission requirements such as minimum GPA/percentage, IELTS/TOEFL,
SAT/TR-YÖS/GRE/GMAT, portfolio/interview requirements, and credit-transfer rules
are explicitly deferred to a separate Admission Requirements capability and
MUST NOT be encoded as ad-hoc ProgramOffering pricing fields.

CAT-025 — TurkDemy MUST provide an `import_programs_for_university` management
command with exactly three required positional inputs: target University ID,
target UniversityCatalogueSource ID, and normalized programme JSON file path.
The source MUST already exist and MUST belong to the supplied University.

CAT-026 — The normalized university-programme JSON contract MUST be explicitly
versioned. Schema v1 MUST support AcademicUnits, optional Departments, Programs,
canonical instruction-language composition, and zero or more ProgramOfferings
using Catalogue v2 field semantics.

CAT-027 — Schema-v1 imports MUST use deterministic update keys: AcademicUnit,
Department, and Program by `slug_en` within the supplied University; Offering by
Program + AcademicYear + Semester + supplied UniversityCatalogueSource. Re-running
the same normalized file MUST update those records rather than creating duplicates.

CAT-028 — For every Program present in a normalized file, the supplied
instruction-language composition MUST be authoritative for that Program and MUST
obey CAT-009/CAT-010. Every imported Offering MUST reference the catalogue source
passed to the command.

CAT-029 — A normalized programme import MUST be atomic. Invalid schema, invalid
references, invalid percentages/pricing/dates, source ownership mismatch, or
ambiguous duplicate database matches MUST stop the import rather than partially
writing or silently choosing a record. Rows absent from the file MUST NOT be
deleted or deactivated automatically.

CAT-030 — The normalized JSON contract and management-command usage MUST be
documented with a complete example file and covered by tests for creation,
idempotent update, source ownership, validation rollback, and duplicate-key
rejection.

CAT-031 — Program MUST provide an optional `internal_notes` field for staff/import
context that is distinct from localized customer-facing descriptions.
`internal_notes` MUST NOT be exposed on public or customer-facing templates or
through the public Program API serializer. Schema-v1 normalized programme JSON
MAY provide `internal_notes`, and the importer MUST create/update that field when
present.

CAT-032 — TurkDemy MUST provide a `dump_university_data` management command whose
only required input is a University ID. The command MUST write a versioned UTF-8
JSON export of that University's catalogue-domain data, including localized
University, geography, AcademicUnit, Department, Program, instruction-language,
ProgramOffering, UniversityCatalogueSource, and UniversityMedia fields needed for
offline comparison/enrichment. The export MUST include Program `internal_notes`
for staff/import analysis, MUST preserve identifiers and structured catalogue
values, and MUST exclude applicant, student, application, messaging, and other
customer operational data.

CAT-033 — Localized catalogue slugs MUST support native Unicode characters for
Persian, Turkish, and Arabic values while `slug_en` MUST retain the existing
ASCII slug validation. This rule applies consistently to catalogue entities that
use the shared localized-slug contract, including University, AcademicUnit,
Department, ProgramLanguage, Program, and their geography dependencies. Admin
validation, normalized JSON import model validation, and public/API routing MUST
accept valid native-script localized slugs without requiring transliteration to
English.

CAT-034 — When an admin/staff user saves a model with a supported slug field and
a clear related name field, a blank slug MUST be generated from that name before
persistence. For the shared localized catalogue/geography contract, `slug_en`,
`slug_fa`, `slug_tr`, and `slug_ar` map to the matching `name_*`; English uses
ASCII slug semantics while Persian, Turkish, and Arabic preserve valid Unicode.
The same fill-only behavior MUST cover other current admin-managed slug fields
with an explicit name mapping, including `FAQCategory.key` from `name_en`.
Explicit slugs MUST never be overwritten merely because the related name changes.
Blank source names MUST leave their slug blank. Supported slug fields MUST be
optional in admin/model forms so this generation path can be used.

## Pricing vocabulary

- **Standard/list tuition** — university/list tuition before an applicable offer.
- **Offered/discounted tuition** — current discounted, scholarship-labelled, or
  partner-offered tuition when the source presents it as the payable tuition.
- **Cash/advance-payment tuition** — tuition payable under cash/up-front payment
  terms; it is not a deposit.
- **Deposit** — amount required to reserve/start the admission process; it is not
  the full advance-payment tuition.
- **Preparatory tuition** — tuition for language/foundation preparation.

Source terminology such as "Scholarship" or "Advance Payment Fee" SHOULD be
preserved in source/notes where its exact business meaning is not fully encoded
by the structured price fields.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by named tests. Migration tests must prove preservation of existing
data. Import tests must cover mixed languages, fractional duration, source
provenance, and distinct tuition/cash/deposit semantics.

## Non-goals

- Deep arbitrary university organisation trees beyond one AcademicUnit level.
- A generic unlimited price-component engine in this iteration.
- Admission-requirement modelling (CAT-024).
- Commission, agent revenue, invoicing, or settlement accounting.
- Automatic extraction/OCR of arbitrary university PDFs/Excel files.

## Catalogue v3 — intake and extensible fees

CAT-035 — ProgramOffering MUST use Intake as its canonical intake dimension. An Intake MUST bind an academic year and MAY be university-specific; names such as Fall, Spring, September, February, and Academic Intake are data, not enum values. The legacy Semester relation MAY remain temporarily as a compatibility bridge.

CAT-036 — Intake application-open/application-deadline dates, when both known, MUST be chronologically valid. A university-specific Intake attached to an offering MUST belong to that Program's University and its academic year MUST match the offering academic year.

CAT-037 — ProgramOffering MUST support normalized OfferingFee rows so university terminology is preserved without adding a new ProgramOffering column for every fee type. Supported fee semantics MUST include list tuition, discounted tuition, advance payment, cash payment, installment total, deposit, preparatory/foundation, application, registration, and other.

CAT-038 — OfferingFee MUST support amount and/or percentage, ISO-supported currency, fee basis, source label/notes, and optional instruction/preparation language. Language-specific preparatory fees MUST therefore be representable independently.

CAT-039 — Fee basis MUST support annual, semester, whole-program, per-credit, and one-time values.

CAT-040 — Existing ProgramOffering pricing columns and Semester MAY remain as deprecated compatibility bridges while current UI/Application consumers migrate. New normalized imports MUST create canonical Intake and OfferingFee data and MUST preserve the source distinction between advance payment and deposit.

CAT-041 — Django Admin MUST present Catalogue v3 `OfferingFee` rows as the
canonical pricing representation for ProgramOffering maintenance. Program-level
offering inlines MUST show a readable structured-fee summary and direct staff to
the ProgramOffering change page for fee editing. Deprecated fixed pricing fields
and legacy Semester MUST remain available during the transition but MUST be
visually separated and collapsed under an explicit compatibility section so they
are not mistaken for the canonical fee model. Staff MUST also be able to browse
and edit OfferingFee rows directly in Admin.


CAT-042 — Structured fee summaries in Django Admin MUST use a stable semantic
ordering rather than alphabetical fee-type ordering. Tuition/list pricing MUST
appear before advance-payment pricing, and preparatory/foundation pricing MUST
appear after advance-payment pricing. Other supported fee types MUST have a
stable business-readable position so fee tables scan consistently across
universities.

CAT-043 — All current public, customer, agent, Application-admin, and API presentation
consumers MUST use Catalogue v3 Intake and OfferingFee as the canonical offering
representation. Public filters MUST filter by Intake rather than legacy Semester,
and tuition filtering/card/detail presentation MUST derive from active structured
tuition fees. Legacy Semester and fixed ProgramOffering pricing columns MAY remain
for import/backfill compatibility but MUST NOT be read by current UI presentation
paths.

## Catalogue v3 transition completion

CAT-044 through CAT-048 supersede the temporary compatibility allowances in CAT-026, CAT-027, CAT-035, CAT-040, CAT-041, and CAT-043 now that the v3 transition is complete.


CAT-044 — Catalogue v3 MUST be the only persisted catalogue representation. The
legacy `Semester` model, `Program.program_language`, whole-year `Program.duration`,
and fixed pricing/currency/basis fields on `ProgramOffering` MUST NOT remain in
the active model schema.

CAT-045 — Formal Application creation MUST snapshot tuition from the active
structured OfferingFee representation, preferring discounted tuition over list
tuition consistently with catalogue presentation. Application creation MUST fail
when no active amount-bearing tuition fee exists. An active structured deposit
fee, when present, MUST be snapshotted into `Application.deposit`.

CAT-046 — The normalized university-program import contract MUST be v3-native:
no legacy Semester or fixed ProgramOffering pricing fields may be persisted. The
current schema MUST identify offerings by `intake` and carry pricing through a
`fees` array whose rows define fee type, currency and basis explicitly.

CAT-047 — The Rasa catalogue importer MUST create university/year-specific Intake
and structured OfferingFee rows directly and MUST NOT recreate Catalogue v2
compatibility data.

CAT-048 — Catalogue maintenance and export surfaces MUST expose only the v3
representation. Django Admin MUST not expose a legacy compatibility pricing
section, and university catalogue dumps MUST export Intake and structured fees
without legacy Program/ProgramOffering compatibility fields.

CAT-049 — Existing databases MUST have a safe pre-migration cutover path before
Catalogue v2 columns/tables are dropped. The cutover MUST preserve already
canonical v3 data, backfill only missing Intake/language/duration/fee data, and
MUST fail rather than drop an offering that still cannot be assigned an Intake.

CAT-050 — Program public slugs MUST be globally unique and MUST be canonicalized
per locale as `<University.slug_LOCALE>-<program-slug-part_LOCALE>`. The same
localized University prefix rule applies to English, Persian, Turkish, and Arabic.
Canonicalization MUST be idempotent and MUST NOT duplicate an already-present
University prefix. Public/API program routes MAY therefore continue resolving a
Program from one localized slug without a separate University route segment.
TurkDemy MUST provide an operator command that can dry-run and rebuild existing
Program slugs to this canonical form before uniqueness constraints are applied.
