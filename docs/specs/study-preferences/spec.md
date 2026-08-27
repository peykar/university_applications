# Applicant study preferences

Status: BASELINED
Version: 1.0

## Goal

Define the established TurkDemy behavior for applicant study preferences.

## Requirements

PREF-001 — A Lead MAY have one optional Study Preference record.

PREF-002 — Preferences MAY include tuition range/currency, languages, cities,
universities, departments, degree types, university types, dormitory/Erasmus
needs and notes.

PREF-003 — When both tuition bounds exist, maximum MUST NOT be below minimum.

PREF-004 — Preference absence MUST NOT prevent Lead creation.

PREF-005 — Preferences are discovery/advisory constraints and MUST NOT themselves
create Program interests or Applications.

## Acceptance policy

Each requirement is accepted when its observable behavior is implemented and
covered by appropriate tests. Negative authorization and invalid-state paths are
part of acceptance when relevant.

## Non-goals

This baseline does not authorize new domain behavior beyond the requirements
above. New behavior requires a spec change before implementation.
