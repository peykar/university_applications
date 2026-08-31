# BUG-0025 — Structured fee order test missing offering fixture

## Problem

The semantic structured-fee ordering regression test was added to
`CatalogueV3AdminPresentationTests`, but that test class did not create a
`ProgramOffering`. The test referenced `self.offering`, causing the full suite
to fail with `AttributeError` before the ordering assertion could run.

## Fix

Add an explicit Catalogue v3 program/offering fixture to the admin presentation
test class. The production semantic ordering behavior is unchanged.

## Verification

The regression test now has the database objects it needs to create Tuition,
Advance Payment, and Preparatory `OfferingFee` rows and verify their rendered
order.
