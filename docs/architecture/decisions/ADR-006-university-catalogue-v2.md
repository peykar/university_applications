# ADR-006 — Model university catalogue identity separately from intake commercial data

Status: ACCEPTED
Date: 2026-08-29

## Context

University/agent price lists supplied to TurkDemy contain stable academic
identity (academic unit, programme, degree, instruction languages, study mode,
duration) alongside intake/version-specific commercial terms (academic year,
intake, tuition variants, deposit, preparation fee, deadline and notes). They
also use mixed languages, fractional durations, and source-specific labels such
as scholarship or advance-payment fee.

The existing Program/ProgramOffering split is sound but the Program side lacks
AcademicUnit, mixed-language composition and study mode, while Offering lacks
explicit source/version metadata and clear preparation semantics.

## Decision

Keep `Program` as stable academic identity and `ProgramOffering` as the concrete
intake/commercial boundary. Extend the catalogue with AcademicUnit,
ProgramInstructionLanguage, structured study mode and fraction-safe duration.
Add UniversityCatalogueSource and link Offerings to provenance. Retain explicit
pricing columns rather than introducing a generic price-component engine in v2.
Rename the misleading preschool fee to preparatory tuition.

Admission requirements are a separate domain concern and are not folded into
ProgramOffering.

## Consequences

- Existing Application and LeadProgramInterest relationships remain stable.
- Catalogue migrations must be compatibility-first and data preserving.
- Public filters and imports must move from the legacy single-language/duration
  paths to canonical structures before legacy fields are removed.
- Source ambiguity is preserved rather than guessed.
- A future Admission Requirements capability can evolve independently.
