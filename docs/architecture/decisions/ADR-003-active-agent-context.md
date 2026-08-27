# ADR-003: One active Agent organization per Agent workspace

Status: Accepted

## Context

A User may belong to multiple Agent organizations. Aggregating their records in
one workspace creates ambiguous authorization and operational context.

## Decision

Every Agent workspace session has exactly one active Agent. Membership is
revalidated on use. One membership auto-selects; multiple memberships require a
valid previous selection or explicit choice.

## Consequences

- All Agent workspace queries are scoped to active Agent.
- Sidebar identifies the active organization.
- Switching organization cannot carry entity-detail URLs across organizations.
