# Models

## BaseModel

All business/domain models use UUID primary keys and audit timestamps.

Audit user references:
- `created_by`
- `updated_by`

Both use `related_name="+"`, which intentionally disables reverse relations
on the user model.

## User

Custom authentication model.

Identity fields include:
- username
- email
- cell
- Telegram username
- Telegram ID

Phone numbers are normalized to E.164 where present.

`cell_verified_at` represents ownership verification state.

## Agent

Represents an agency/company.

Fields and relationships:
- `company_name`
- optional `logo`
- optional `email`
- optional `website`
- optional `cell`
- optional `landline`
- `users` — many-to-many relationship to the custom user model
- optional `parent` agent
- `is_active`

Phone numbers are validated and normalized to E.164.

An agent is not tied to a single user. Multiple users can belong to the same
agent organization.

Agents can still form a hierarchy using:

```text
Agent
└── parent → Agent
```

## AgentDocument

Stores internal documents belonging to an agent.

Examples:
- signed agreement with the agent
- payment receipt
- commission statement
- contract attachment
- internal supporting document

Fields:
- `agent`
- `name`
- `description`
- `file`
- inherited audit fields

The description is intended for internal staff use.


## Geography

```text
Country
└── Province
    └── City
```

The geography catalogue is primarily used for institutional data such as
university location.

Student residence city is not required to reference `City`.

## University

A university belongs to a `City`.

Important properties include:
- approval/recognition fields are university-level only
- multilingual name and slug
- multilingual description
- logo
- banner
- website
- university type
- YÖK recognition
- Erasmus
- dormitory availability
- ranking fields
- active/featured flags
- `listing_priority` for internal ordering control

## UniversityMedia

Stores multiple university images independently from the main logo/banner.

## Department

A department belongs to one university.

Programs may optionally reference a department.

A program cannot reference a department belonging to another university.

## ProgramLanguage

Reusable language catalogue for programs.

## AcademicYear

Represents values such as:

```text
2026-2027
```

## Semester

Examples:
- Fall
- Spring

## Program

Represents the academic identity of a program.

Important fields include:
- university
- department
- multilingual name/slug/description
- degree
- thesis type
- program language
- duration
- active state

Tuition, quota and deadline do not belong here.

Programs do not carry MOE, MOH, or YÖK approval flags. Those recognition/approval flags belong to `University`.

`Program.listing_priority` is an internal ordering value; higher values can be used to place programs earlier in listings.

## ProgramOffering

Represents a specific academic intake for a program.

Contains:
- program
- academic year
- semester
- fee basis
- currency
- tuition
- discounted tuition
- cash tuition
- installment tuition
- deposit
- pre-school fees
- quota
- deadline
- active state

## Student

Represents an applicant/student.

Important fields include:
- optional linked user
- optional agent
- personal details
- nationality
- birth country
- contact information
- birthdate
- language-test data
- high-school GPA
- parents' names
- passport information
- residence country
- residence city as free text
- address
- educational background
- notes

### High-school GPA fields

`Student.high_school_gpa` stores the student's final high-school grade or GPA
in the original grading system.

`Student.high_school_gpa_scale` stores the maximum value of that grading scale.

Examples: `17.5 / 20`, `3.5 / 4`, `7.8 / 10`, or `87.5 / 100`.

Keeping both values preserves the student's original grading system.

## StudentDocument

Reusable student-owned documents.

The same document may be attached to multiple applications.

## Application

Connects:
- student
- agent
- program offering

It stores tuition/deposit snapshots from the offering so historical
applications are not changed by later fee updates.

## ApplicationDocument

Connects a student's existing document to a particular application.

A document attached to an application must belong to that same student.

Country data is populated from `pycountry` for ISO identity and Babel/CLDR for localized display names.
