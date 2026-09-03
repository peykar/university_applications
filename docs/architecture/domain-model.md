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
 │    ├── structured system event (`event_type` + `event_data`) when applicable
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

Catalogue v3 is the sole active catalogue representation. The canonical domain is:

```text
University
 ├── AcademicUnit / Department
 └── Program
      ├── GeneralField? → TurkDemy-wide curated classification
      ├── ProgramInstructionLanguage → ProgramLanguage
      ├── study mode / duration_months
      └── ProgramOffering
           ├── AcademicYear / Intake
           ├── OfferingFee[]
           ├── quota / deadline / validity
           └── UniversityCatalogueSource
```

Catalogue v2 compatibility models and fields have been removed. Importers, Admin,
exports, UI/API consumers, and Application creation use Intake and OfferingFee.

`GeneralField` is intentionally outside the University hierarchy. It provides one
canonical TurkDemy-wide field identity for public filtering and future field landing
pages. Programme imports do not classify it; TurkDemy admins assign it only after
reviewing the imported catalogue.
