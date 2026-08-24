# TurkDemy Architecture

## Project structure

TurkDemy uses a multi-app Django architecture:

```text
apps/
├── accounts/
├── agents/
├── geography/
├── universities/
├── students/
├── applications/
├── content/
├── health/
└── core/
```

## Domain boundaries

### accounts
Custom `User` and authentication identity fields.

### agents
Education agencies, their users, hierarchy, contact details and internal documents.

### geography
Country, province and city reference data.

### universities
Universities, media, departments, languages, academic years, semesters, programs and offerings.

### students
Student profile and reusable student documents.

### applications
Applications and application-specific document links.

### content
FAQ categories, FAQs and contact submissions.

### health
Operational health/readiness endpoints.

### core
Shared abstract models, localization mixins, phone helpers and validators.

## Project configuration

Settings are split into:

```text
turkdemy/settings/
├── base.py
├── local.py
└── production.py
```

Local development defaults to SQLite.

## Data

`data/rasa/` is reserved for RasaStudy source dumps/assets.
`data/fixtures/` is reserved for project-maintained fixture/reference data.


## Web frontend

Django templates are the primary public frontend. TurkDemy intentionally does
not maintain a separate React/Vite web application.

DRF is retained as an API/integration layer, not as a requirement for the
website itself.
