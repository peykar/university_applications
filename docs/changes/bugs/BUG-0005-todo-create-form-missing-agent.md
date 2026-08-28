# BUG-0005 — TODO create form validates before Agent is attached

Status: DONE
Reported: 2026-08-28
Parent feature: `FEAT-0001-agent-todos-communication-log`

## Report

Posting the global Agent TODO create form raised `RelatedObjectDoesNotExist:
Todo has no agent` during `TodoForm.is_valid()`.

## Classification

BUG

## Violated requirements

- `TODO-001` — a TODO must belong to exactly one Agent organization.
- `TODO-003` — the specified TODO fields must be creatable through the Agent workflow.

## Expected behavior

The active Agent organization is attached to the candidate TODO before model
validation, so assignee membership can be validated and a valid TODO can be
created.

## Actual behavior

`ModelForm._post_clean()` called `Todo.full_clean()` before `create_todo()` ran.
`Todo.clean()` dereferenced `self.agent`, but the ModelForm instance did not yet
have its required Agent assigned.

## Reproduction

1. Open the Agent workspace TODO page.
2. Submit a valid TODO through `/agent/todos/create/`.
3. `TodoForm.is_valid()` enters model validation.
4. `Todo.clean()` accesses `self.agent.users` and raises because `agent` has not
   been assigned to the form instance.

## Root cause

The active Agent was passed to `TodoForm` only to scope the assignee queryset.
It was not assigned to `form.instance` before Django ModelForm model validation.

## Resolution

`TodoForm.__init__()` now assigns the supplied active Agent to
`self.instance.agent` before validation. `Todo.clean()` also guards its
organization-membership check with `self.agent_id`, avoiding a relation
dereference when validating a deliberately incomplete model instance.

## Regression tests

- [x] Form instance receives the active Agent before validation.
- [x] Valid Agent assignee can pass ModelForm validation.
- [x] Model validation does not dereference a missing Agent relation.
- [x] Full local suite confirmed after this patch.

## Spec/design impact

Product spec change: No.

Design update: TODO form validation now explicitly binds the active Agent to the
candidate model instance before `_post_clean()`.

## Verification

- [x] `make format`
- [x] `make check`

Result: PASS. The project owner confirmed `make format` and `make check` both
pass and manually verified TODO creation and the TODO/Communication Log workflows
in the normal development environment on 2026-08-28.
