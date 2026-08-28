# BUG-0006 — Applicant modal actions did not open

Status: VERIFYING
Reported: 2026-08-28

## Classification

BUG

## Expected behavior

Selecting **Finalize applicant** opens the finalization review dialog. Other
Applicant modal actions use the same working trigger behavior.

## Actual behavior

Selecting **Finalize applicant** did nothing.

## Root cause

The Applicant detail template placed its modal JavaScript inside
`{% block agent_title %}`. This page overrides `agent_page_header` with an empty
block. Since `agent_title` is nested inside that overridden parent block, Django
never rendered the JavaScript. The button and dialog existed, but no click
handler called `showModal()`.

## Resolution

Moved the modal JavaScript to the base template's `extra_scripts` block and
preserved `{{ block.super }}`. `agent_title` now contains only the Applicant
title.

## Regression coverage

`AgentFinalizeWorkflowTests` verifies that modal JavaScript is rendered from
`extra_scripts`, is not nested in `agent_title`, and still calls `showModal()`.

## Spec impact

No product specification change. This restores the already specified
finalization interaction.

## Verification

- Static validation: PASS.
- Full local `make format` / `make check`: pending.
