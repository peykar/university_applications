# Architecture overview

TurkDemy is a Django 5.2 multi-app admissions platform.

## Layers

```text
Public catalogue / authenticated workspaces
                 |
              views/forms
                 |
          domain/service layer
                 |
             Django ORM
                 |
     PostgreSQL / configured database
```

The project currently uses server-rendered Django templates for the authenticated
workspace behavior covered by these specs. Public UI architecture is documented
separately in the existing project docs.

## Domain apps

- `accounts` — custom User and authentication integration.
- `agents` — Agent organizations and Agent workspace.
- `leads` — Applicants, preferences, interests, Lead documents and activities.
- `students` — finalized Students and reusable Student documents.
- `applications` — formal Applications and application-scoped documents.
- `messaging` — generic subject-scoped conversations/messages/read state.
- `universities` — Universities, Programs and ProgramOfferings.
- `geography` — Country/Province/City catalogue.
- `content` / `public` — public content/discovery surfaces.
- `core` — shared base concerns.
- `api` — API surface.

## Architectural boundaries

1. Product rules live in specs and domain/service code, not only templates.
2. Views authorize and orchestrate; reusable workflow logic belongs in services.
3. Cross-model state transitions that must succeed together use transaction
   boundaries.
4. Agent workspace authorization always starts from the active Agent context.
5. Generic messaging must not be re-specialized into duplicate Lead-only message
   models.
6. A model transition (Lead→Student) does not require a new user-facing person
   navigation boundary.

## Existing canonical services

Important established services include:

- Lead finalization/conversion service.
- Student application creation service.
- Agent active-context resolver.
- Generic messaging services.
- Shared applicant activity/audit recorder.

Design specs should reuse these rather than reproducing their rules in views.
