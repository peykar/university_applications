# Agent Operations Workspace

V1 adds two Agent-private operational capabilities:

- **Todos** — shared Agent-organization work items with optional generic subject,
  assignee, date-only due date, lifecycle and immutable comments.
- **Communication Log** — CRM history for phone/email/WhatsApp/Telegram/in-person/
  video/other communication outside TurkDemy Messages, with creator-only edits
  and immutable revision snapshots.

## Navigation

Agent sidebar:

`Overview → Applicants → Applications → Todos → Communications → Messages`

Applicant Agent tabs add `Todos` and `Communication Log`. Applicant scope
aggregates direct Applicant entries plus entries whose canonical subject is one
of that Applicant's Applications.

Application Agent tabs add `Todos` and `Communication Log` for that Application.

## Database setup

This repository's current fresh-start baseline intentionally contains no
generated project migration history. After pulling this feature in a normal
development environment, run:

```bash
make makemigrations
make migrate
```

Review the generated migration set before committing/deploying it.

## V1 exclusions

No reminders, attachments, multiple TODO assignees, structured University
counterparty FK, or merged Message/Communication persistence.
