# UI-0007 — Collapse empty workspace secondary sidebars

Status: IMPLEMENTED

## Problem

The shared workspace geometry could reserve a secondary/context column even when there was no meaningful context to show. This left the central workspace unnecessarily narrow and created visible empty space.

## Decision

Optional secondary/context sidebars are content-driven. When no meaningful secondary content exists, do not render the sidebar and expand the primary/middle workspace into that width. This is a shared customer/Agent workspace rule.

## Implementation

- Added `NAV-012` / `NAV-T12`.
- Customer Request context now exposes `has_request_context_data` from structured document/preference data.
- Overview, Profile, Programs, and Messages render the context rail only when that data exists.
- When absent, `request-detail-layout-full` gives the central workspace the full available width.
- Documents and Preferences retain their existing intentional full-width behavior.

## Verification

Covered by `CustomerRequestWorkspaceTests.test_empty_request_context_releases_secondary_column` plus SDD validation and project checks.
