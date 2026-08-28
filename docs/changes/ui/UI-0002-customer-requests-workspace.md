# UI-0002 — Customer Requests workspace redesign

Status: IMPLEMENTED

## Summary

Redesigned the authenticated customer workspace around a single customer-facing
**Request** abstraction. Internal Lead/Student/Application lifecycle terminology
remains unchanged for Agent/domain workflows.

## Changes

- Customer sidebar is menu-only: My Requests, Messages, Get Help, optional WhatsApp.
- Removed “MY TURKDEMY” / “Student workspace” sidebar copy.
- My Requests is the authenticated customer landing page.
- Added Find Programs as the My Requests page action.
- Request cards show full name, email, cell, all associated program interests,
  and a small Agent-suggestion tip where relevant.
- Cards show action-required signals for unread incoming messages and documents
  requiring replacement.
- Entire request card is clickable.
- WhatsApp number comes from `WHATSAPP_NUMBER`; no number is hard-coded.
- Customer shared request headers/navigation use Request terminology while Agent
  Applicant navigation remains operationally unchanged.

## SDD

See `docs/specs/customer-requests/` (`CRQ-001`–`CRQ-010`).
