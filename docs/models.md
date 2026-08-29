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
- Semester
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

## Catalogue v2 notes

`Program` is the stable academic identity. Canonical programme dimensions are
`academic_unit`, optional `department`, `degree`, `thesis_type`, `study_mode`,
`duration_months`, and the `ProgramInstructionLanguage` through rows. Program also
has `internal_notes` for staff/import context; it is deliberately excluded from
public/customer presentation and the public Program API. The old `program_language`
and whole-year `duration` fields remain compatibility bridges for existing
databases/import data and are not customer-facing canonical fields.

`ProgramOffering` owns intake/commercial data. `preparatory_tuition` is the
domain-facing name for the historic `pre_school_fees` database column. Standard
tuition, discounted/offered tuition, cash/advance-payment tuition, deposit, and
preparatory tuition have distinct meanings.
