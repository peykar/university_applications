# Domain model

## Core admissions path

```text
User
 └── owns/manages ──> Lead (Applicant)
                       ├── LeadPreference
                       ├── LeadProgramInterest ──> Program
                       │                         └── ProgramOffering? (optional)
                       ├── LeadDocument
                       ├── LeadActivity
                       └── converted_student ──> Student
                                                  ├── StudentDocument
                                                  └── Application
                                                       ├── ProgramOffering
                                                       │    └── Program
                                                       │         └── University
                                                       └── ApplicationDocument
```

The Lead→Student transition is a workflow boundary. `LeadProgramInterest` remains
historical/exploratory; an Application is a distinct formal record.

## Agent organization

```text
User >──< Agent
           ├── Leads
           ├── Students
           ├── Applications
           └── Conversations
```

A User can belong to multiple Agents. One Agent is active in an Agent workspace
session.

`Lead.assigned_to -> User` identifies the responsible user; it is not the
authorization boundary for other users of that Agent.

## Messaging

```text
Conversation
 ├── Agent
 ├── customer User
 ├── subject_content_type
 ├── subject_object_id
 ├── Message*
 │    └── MessageAttachment*
 └── ConversationParticipantState*
      ├── User
      ├── participant_role
      └── last_read_message / last_read_at
```

Subjects can be Lead, Student, Application, or future supported domain concepts.

## Documents

```text
LeadDocument
 ├── review state
 ├── version history
 └── review history

Student
 └── StudentDocument*  (reusable master documents)

Application
 └── ApplicationDocument*
      └── StudentDocument? (must belong to same Student)
```

Document attachment and document requirement are separate concepts.

## Catalogue

Catalogue v2 is implemented. The canonical domain is:

```text
University
 ├── AcademicUnit*
 ├── Department*
 ├── UniversityCatalogueSource*
 └── Program*
      ├── AcademicUnit?
      ├── Department?
      ├── ProgramInstructionLanguage* -> ProgramLanguage
      ├── study mode / duration
      ├── internal_notes (staff/import only)
      └── ProgramOffering*
           ├── AcademicYear / Semester
           ├── standard / offered / cash tuition / deposit
           ├── preparatory tuition / preparation included
           ├── quota / deadline / validity / notes
           └── source? -> UniversityCatalogueSource
```

Legacy single-language and whole-year duration fields remain executable compatibility
bridges during migration. Existing databases should run `backfill_catalogue_v2` after
applying schema migrations. See `docs/specs/catalogue/` and ADR-006.
