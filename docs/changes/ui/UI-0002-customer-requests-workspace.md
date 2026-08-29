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

See `docs/specs/customer-requests/` (`CRQ-001`–`CRQ-019`).

- Fixed Applied for entries to render the actual program and university names instead of separator-only boxes caused by nonexistent `.name` template attributes.
- Removed request-card hover movement, border/shadow changes, and inherited link underlining.

- Redesigned Request detail into a central workspace plus persistent right context sidebar.
- Kept Request tabs (Overview, Profile, Programs, Documents, Messages) between the Request header and active content.
- Added Uploaded documents and Program preferences to the right context sidebar across Request tabs.
- Rebuilt Overview around action-required items, applied-for programs, customer-safe progress and recent messages.
- Opening Overview no longer consumes unread-message state; Request Messages remains the read boundary.
- Customer status labels now present Received / In progress / Completed / Closed while internal Lead states remain unchanged.

- Reserved a distinct logical inline action lane on Programs cards so the Program Detail arrow and gray trash action no longer crowd each other in LTR or RTL.
- Replaced the Programs-card raw arrow and underspecified trash action with matched circular SVG icon controls: blue-toned Program Detail navigation and a distinct destructive Remove action.
