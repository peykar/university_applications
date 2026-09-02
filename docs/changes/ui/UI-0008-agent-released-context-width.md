# UI-0008 — Agent workspace uses released context width

Status: IMPLEMENTED

## Problem

Agent pages without a secondary/context sidebar rendered no empty sidebar element, but the outer Agent canvas still stopped at the narrower standard site-container boundary. On wide desktop screens this made the main section look as though the absent context rail was still reserved as empty space.

## Decision

The Agent workspace keeps the shared TurkDemy workspace visual language and the primary sidebar's standard inline-start alignment, while its desktop canvas may extend toward the inline-end viewport edge up to the width of the normal content area plus one context rail and gap. When no context rail is present, main content consumes that space.

## Affected Agent pages without a secondary/context rail

- Operations Overview
- Applicants list
- Applications list
- TODOs
- Communications
- Messages inbox
- Applicant focused sections that do not render a context rail
- Application focused sections that do not render a context rail

Entity pages with a real secondary rail keep it and can use the same expanded desktop canvas.

## Implementation

- Added `NAV-013` / `NAV-T13`.
- Added a desktop-only Agent page-shell width rule.
- Kept the Agent workspace inline-start aligned with the standard 1160px site container.
- Allowed inline-end growth up to 1496px, corresponding to the standard canvas plus a 310px context rail and 26px gap.
- Kept existing tablet/mobile workspace collapse unchanged.

## Verification

Covered by `NavigationArchitectureTests.test_agent_workspace_expands_into_released_context_space`, SDD validation, formatting, and project checks.
