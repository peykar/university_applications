# BUG-0001 — Applicant edit i18n template error

Status: VERIFYING
Reported: 2026-08-28
Parent change: `UI-0001-full-page-applicant-editor`

## Report

Opening the Agent Applicant edit page raised `TemplateSyntaxError` because the
included field partial used `{% trans %}` without loading the i18n tag library.

## Classification

BUG

## Affected requirements

- APL-003 — authorized Agent Applicant editing must be usable.
- NAV-004 — Applicant Profile edit entry must resolve to a working page.

## Expected behavior

GET Applicant edit page renders normally.

## Actual behavior

Django raised `Invalid block tag: 'trans'`.

## Root cause

`templates/agents/includes/applicant_edit_field.html` did not contain
`{% load i18n %}`. Included Django templates have their own tag-library parsing
context.

## Resolution

Added `{% load i18n %}` to the partial and a regression assertion.

## Regression tests

- `AgentEditUploadWorkflowTests.test_edit_field_partial_loads_i18n_tag_library`

## Spec/design impact

Product spec change: No.

## Verification

- Static/source validation: PASS.
- Full local `make check`: pending confirmation after the latest combined patch.
