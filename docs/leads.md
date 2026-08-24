# Lead / Applicant Workflow

TurkDemy uses **Lead** internally and **Applicant** in the customer UI.

## Core distinction

```text
User
= authenticated account / customer

Lead
= provisional applicant managed by that account

Student
= validated canonical applicant

Application
= formal application to a ProgramOffering
```

One User may own/manage any number of Leads and, after conversion, any number
of Students.

Anonymous visitors can browse the catalogue, but they must log in before
creating applicants or applying/expressing interest in a program.

## Models

```text
Lead
├── LeadPreference
├── LeadProgramInterest
├── LeadDocument
├── LeadActivity
└── LeadConversation
     └── LeadMessage
          ├── LeadMessageAttachment
          └── LeadMessageRead
```

### Lead

Stores provisional applicant data. Phone/passport/email values are not treated
as validated canonical identity data merely because they were entered.

`needs_program_recommendation=True` means the applicant does not know which
programs fit and wants TurkDemy staff/system to investigate.

### LeadPreference

Broad criteria:
- tuition min/max + currency
- degrees
- program languages
- cities
- universities
- departments/fields
- university types
- dormitory preference
- Erasmus preference
- additional notes

### LeadProgramInterest

Specific program choices or recommendations.

Sources:
- `user`
- `agent`
- `system`

Statuses:
- suggested
- interested
- shortlisted
- declined
- qualified
- converted

Agent/system suggestions appear in the customer's Applicant workspace. The
customer can mark a suggestion as interested or decline it.

A formal Application is created only from a **qualified** interest with a
specific ProgramOffering.

### Messaging

Each Lead has exactly one LeadConversation. User and staff/system messages,
attachments and per-user read receipts remain tied to that applicant.

LeadActivity is separate: it is workflow/audit history and may be internal.
It must not be confused with customer-visible chat.

## Finalization and conversion

The conversion is explicit and transactional; it is not implemented in
`Lead.save()` or a model signal.

```text
Lead
  ↓ staff/system validates data
FINALIZED
  ↓ convert_lead_to_student()
Student
  +
qualified LeadProgramInterest(s)
  ↓
Application(s)
```

`finalize_lead()` requires at least:
- first name
- last name
- validated nationality
- validated gender

`convert_lead_to_student()`:
1. requires a finalized lead
2. creates or reuses `Lead.converted_student`
3. maps validated applicant data into Student
4. copies verified LeadDocuments into StudentDocuments
5. converts qualified interests into draft Applications
6. links each converted interest to its Application
7. preserves the original Lead permanently
8. records customer-visible activity/system messages

Re-running conversion is safe for an already converted lead and can convert
newly qualified interests without creating another Student.

## Recommendations

`recommend_programs_for_lead()` uses stored LeadPreference criteria to generate
deterministic system suggestions. It does not silently decide eligibility.

Staff can run the admin action **Generate system program recommendations**.

## Staff admin workflow

Lead Admin includes:
- study preference inline
- program-interest inline
- document inline
- readonly activity history
- recommendation generation
- finalization
- Lead → Student conversion

Before converting, staff should:
1. validate applicant data
2. verify relevant documents
3. choose ProgramOffering for interests that will become Applications
4. mark those interests `QUALIFIED`
5. finalize the Lead
6. convert it
