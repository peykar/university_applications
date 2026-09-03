# TurkDemy Models

## accounts
- User

## agents
- Agent
- AgentDocument

## geography
- Country
- Province
- City

## universities
- University
- UniversityMedia
- Department
- AcademicUnit
- ProgramLanguage
- ProgramInstructionLanguage
- AcademicYear
- Intake
- OfferingFee
- Program
- ProgramOffering
- UniversityCatalogueSource

## students
- Student
- StudentDocument

## applications
- Application
- ApplicationDocument

## content
- FAQCategory
- FAQ
- ContactSubmission

## Key relationships

```text
Country → Province → City → University
University → AcademicUnit / Department
University → UniversityCatalogueSource
University → Program → ProgramInstructionLanguage → ProgramLanguage
University → Program → ProgramOffering → Application
ProgramOffering → UniversityCatalogueSource (optional provenance)
Agent → Student → Application
Student → StudentDocument → ApplicationDocument → Application
```

## Catalogue v3 notes

`Program` is the stable academic identity. Canonical programme dimensions are
`academic_unit`, optional `department`, `degree`, `thesis_type`, `study_mode`,
`duration_months`, and `ProgramInstructionLanguage` through rows. `internal_notes`
is staff/import-only. Catalogue v2 compatibility fields have been removed.

`ProgramOffering` owns the academic year, canonical `Intake`, availability,
provenance, and preparation-inclusion metadata. All prices, currencies,
percentages, and fee bases are represented only by `OfferingFee` rows.

Localized catalogue slugs use ASCII `slug_en` as the deterministic import key;
localized Persian/Turkish/Arabic slugs may use native Unicode.

### Automatic localized slugs

Catalogue/geography models that use `LocalizedNameMixin` + `LocalizedSlugMixin`
auto-fill blank slug fields from the corresponding localized name before save.
The same shared mechanism fills `FAQCategory.key` from `name_en`. The behavior is
fill-only and never overwrites an explicit stored slug.

## Catalogue v3 pricing/intakes

`Intake` is the sole offering intake entity. `OfferingFee` is the sole monetary
representation and supports list/discounted tuition, advance/cash payment,
installment total, deposit, preparatory/foundation, application, registration,
and other fees. Django Admin and UI/API readers use these canonical rows directly.

Formal Application creation snapshots the active discounted tuition when present,
otherwise list tuition, and snapshots an active structured deposit when present.
An offering without an active amount-bearing tuition fee cannot start an Application.



### City public media

`City` stores an optional `banner` (`cities/banners/`) plus `banner_alt_en`,
`banner_alt_fa`, `banner_alt_tr`, and `banner_alt_ar`. `localized_banner_alt` uses the
active locale, then English, then the localized City name.
