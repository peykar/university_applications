# Business Rules

## Programs

- A `Program` belongs to one university.
- If a program references a department, that department must belong to the
  same university.
- Thesis type is only meaningful for degree types that support it.

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

