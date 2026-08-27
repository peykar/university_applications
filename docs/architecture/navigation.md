# Navigation architecture

TurkDemy uses four conceptual navigation levels.

## L1 — Global

Public discovery and account/workspace entry:

- Universities
- Programs
- FAQ
- About
- My TurkDemy
- account/sign-in controls

## L2 — Workspace

### My TurkDemy

- Overview
- Applicants
- Messages
- workspace switch

### Agent workspace

- active Agent identity
- organization switcher when multiple memberships exist
- Overview
- Applicants
- Applications
- Messages
- My TurkDemy switch

## L3 — Entity context

### Applicant

- Overview
- Profile
- Programs
- Documents
- Applications
- Messages

Activity remains available to Agent users as an audit destination.

### Application

- Overview
- Requirements
- Documents
- Activity
- Messages

## L4 — record/action

A specific document, message action, edit form or workflow action should normally
use breadcrumbs, modal/action UI or a focused page. Do not create another
permanent navigation bar without a new information-architecture decision.

## Scope rule

Similar labels at different levels have different scopes:

- Agent sidebar Applications = all Applications in active Agent.
- Applicant → Applications = Applications for that Applicant/Student.
- Application → Documents = documents for that one Application.
- Global/workspace Messages = inbox.
- Applicant/Application Messages = subject-scoped conversation.

Lead→Student conversion does not replace Applicant entity navigation with a
separate permanent Student navigation identity.
