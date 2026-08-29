# UI-0003 — Request Preferences tab

Status: IMPLEMENTED
Date: 2026-08-29

## Change

Promote customer Program preferences from sidebar-only access to a first-class **Preferences** Request tab. The tab is read-only by default, exposes a shared **Edit preferences →** page action for mutable Requests, and owns the complete preference presentation without duplicating the Request context sidebar.

## SDD

Customer Requests v1.27: CRQ-087 through CRQ-090; CRQ-073 revised for six-tab mobile navigation.

## Verification

Covered by named structural/style tests in `tests/test_customer_request_workspace.py` and finalized-mutation guard coverage in `tests/test_finalized_customer_lead_mutations.py`.
