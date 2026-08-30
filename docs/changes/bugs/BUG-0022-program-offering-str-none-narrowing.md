# BUG-0022 — ProgramOffering `__str__` nullable relation typing

## Symptom

`make check` failed in mypy because checking `intake_id` / `semester_id` does not narrow the corresponding nullable Django relation for django-stubs.

## Fix

`ProgramOffering.__str__` now binds the optional related objects to local variables and explicitly checks them against `None` before accessing `name_en`. Runtime behavior is unchanged.

## Verification

Repository SDD validation and Python compilation pass in the delivery environment. Full local `make check` should be rerun by the operator.
