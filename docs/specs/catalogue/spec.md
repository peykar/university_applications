# University and program catalogue

Status: APPROVED
Version: 2.0

## Goal

Model university-supplied programme catalogues and agent tuition sheets without
flattening stable academic identity, intake-specific commercial terms, or source
provenance. The catalogue must support the structures observed in university
price lists while remaining suitable for public discovery and admissions.

## Requirements

CAT-001 — A Program MUST belong to one University.

CAT-002 — A Program Department, when present, MUST belong to the same University.

CAT-003 — ProgramOffering MUST hold intake-specific academic year, semester,
tuition and applicable quota/deadline data.

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
