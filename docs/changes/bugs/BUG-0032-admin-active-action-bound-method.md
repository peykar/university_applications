# BUG-0032 — Shared active/inactive admin actions receive an extra argument

Status: DONE
Classification: BUG
Owning capability: Core/admin infrastructure

## Report

Submitting the shared `mark_active` or `mark_inactive` Django admin action could
raise `TypeError: ActiveActionsMixin.mark_inactive() takes 3 positional arguments
but 4 were given`.

## Cause

`ActiveActionsMixin.get_actions()` manually registered `self.mark_active` and
`self.mark_inactive`. Those are bound methods. Django admin action dispatch calls
the registered callable with the `ModelAdmin` instance, request and queryset, so
the already-bound method received the admin instance a second time.

## Implementation

The shared actions are now registered as unbound mixin methods. Django can call
them with its standard `(model_admin, request, queryset)` action signature.
This keeps the shared actions available to all admin classes using the mixin and
does not change database schema or action semantics.

## Regression coverage

`tests/test_active_admin_actions.py` resolves both actions through
`get_actions()` with a real `RequestFactory` GET request and invokes them exactly
as Django admin dispatch does, verifying that each action updates the queryset
without an argument-count error. Using a real request also exercises Django's action discovery contract (`request.GET`) instead of relying on an unconstrained
mock.
