# Architecture

## Overview

The project is a Django application for managing university applications.

The main domain flow is:

```text
User
├── Agent membership (many-to-many)
│   └── Agent
│       └── parent → Agent
└── Student
    ├── StudentDocument
    └── Application
        └── ProgramOffering
            └── Program
                ├── University
                ├── Department
                └── ProgramLanguage

Country
└── Province
    └── City
        └── University
```

## Main design boundaries

### Program vs ProgramOffering

`Program` represents the academic identity of a degree program.

Examples:
- Computer Engineering
- Bachelor
- English
- 4 years

`ProgramOffering` represents a specific intake/admission opportunity.

Examples:
- academic year
- semester
- tuition
- discount
- currency
- quota
- deadline

Applications reference `ProgramOffering`, not only `Program`.

### Student location

`country_of_residence` references the project `Country` catalogue.

`city_of_residence` is intentionally free text because the system does not
maintain a complete catalogue of every city in every country.

### Audit fields

Business models inherit `BaseModel` and receive:
- UUID primary key
- created_at
- updated_at
- created_by
- updated_by

The audit user foreign keys use `related_name="+"`, so no reverse audit
relations are added to the custom user model.

### Agent organization model

`Agent` represents an agency/company rather than a single user's profile.

An agent has:
- `company_name`
- optional `logo`
- zero or more associated users
- optional parent agent

Users and agents use a many-to-many relationship so multiple staff accounts
may operate under the same agency and a user may be associated with more than
one agency when needed.
