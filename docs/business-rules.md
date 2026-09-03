# Business Rules

## Programs

- A `Program` belongs to one university.
- If a program references a department, that department must belong to the
  same university.
- Thesis type is only meaningful for degree types that support it.
- `GeneralField` is a TurkDemy-wide curated classification, separate from a
  University's AcademicUnit/Department structure.
- `import_programs_for_university` never maps or clears `Program.general_fields`;
  new Programs start unmapped and re-imports preserve manual assignments.

## Program offerings

- Intake-specific tuition, quota and deadline belong to `ProgramOffering`.
- Applications reference `ProgramOffering`.

## Applications

- Tuition and deposit stored on `Application` are snapshots.
- Updating a later `ProgramOffering` price must not retroactively change
  an existing application's agreed values.

## Documents

- Student documents are reusable.
- An `ApplicationDocument` may only reference a `StudentDocument` owned by
  the same student as the application.

## Residence city

- `Student.country_of_residence` uses the country catalogue.
- `Student.city_of_residence` is free text.
- The system must not require a complete worldwide city catalogue.

## Audit relations

- `created_by` and `updated_by` retain forward foreign keys to `User`.
- Neither creates a reverse relation on `User`.

## Agents

- `Agent` represents a company/agency, not a single user profile.
- Each agent has a required company name.
- Logo, email and website are optional.
- Cell/mobile and landline numbers are optional.
- Phone numbers are validated and normalized to E.164.
- An agent may have multiple users.
- A user may be associated with multiple agents.
- Parent/sub-agent hierarchy remains supported.
- Internal agent documents are stored through `AgentDocument`.
- `AgentDocument.description` is internal staff-facing metadata.

## University approval and recognition

- `is_yok_recognized` belongs to `University`.
- `is_moe_approved` belongs to `University`.
- `is_moh_approved` belongs to `University`.
- `Program` must not duplicate these fields.

## Listing priority

- `University.listing_priority` and `Program.listing_priority` are internal
  integer ordering controls.
- The default value is `0`.
- Higher values indicate greater listing priority.
- The field does not imply sponsorship, popularity, quality, or academic rank.
- Public listing/query logic may use it as an ordering input; it is not a
  replacement for search relevance or explicit academic ranking fields.

## FAQs and contact submissions

- An FAQ category must have at least one localized name.
- An FAQ must have at least one localized question and one localized answer.
- FAQ category counts are computed from related FAQ rows rather than manually stored.
- Contact phone numbers, when supplied, must use a valid international phone format and are normalized to E.164.
- `ContactSubmission.handled` is an internal workflow flag and does not turn a contact message into an admissions application.
