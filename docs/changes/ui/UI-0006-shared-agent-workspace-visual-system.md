# UI-0006 — Shared Agent workspace visual system

Status: DONE  
Classification: UI  
Owning capability: Navigation and workspaces  
Affected requirement: NAV-011  
Task: NAV-T11

## Request

Make the Agent workspace follow the same overall look and structural design
language as the customer My TurkDemy workspace.

## Decision

Treat My TurkDemy and Agent workspace as role-specific variants of one shared
TurkDemy workspace visual system. They share the standard site container, desktop
sidebar geometry, main-content spacing, page-heading hierarchy, entity navigation,
responsive collapse, and RTL behavior.

Visual parity does not collapse the two information architectures. Agent active
organization identity/switching, operational navigation, permissions, panels, and
data density remain Agent-specific.

## Implementation

- Removed the Agent-only 1500px container and custom workspace-grid/page-shell
  spacing overrides so Agent pages inherit the shared workspace shell.
- Removed the duplicate `AGENT WORKSPACE` eyebrow from standard Agent page
  headings and use the same section-heading hierarchy as customer workspace pages.
- Aligned narrow-screen Agent workspace navigation with the same adaptive grid
  used by My TurkDemy, so labels can wrap and actions do not clip off-screen.
- Kept Agent organization identity, organization switcher, Agent navigation,
  entity navigation, operational controls, and existing workflows intact.
- Updated navigation and Agent workspace documentation and structural tests.

## Verification

Run `make format` and `make check`.
