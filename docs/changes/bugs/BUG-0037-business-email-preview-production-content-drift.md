# BUG-0037 — Business email previews did not show production content

Status: IMPLEMENTED
Date: 2026-09-10
Capability: Email and notification templates

## Problem

The Email Preview Gallery registered the new business notification types but rendered a generic
"representative preview" body for them. This made the canonical preview surface differ from the
actual subject/body content sent by production workflows. The shared branded email footer also
contained untranslated English text when previewing non-English languages.

## Decision

Business email copy is now built by one shared production/preview content builder. Production
notification delivery and the Email Preview Gallery both call that builder; previews provide
realistic sample values and localized deep-link examples. Shared email chrome is translated in the
active email language.

## SDD impact

- Added `MAIL-017` requiring production-parity business previews.
- Added `MAIL-018` requiring localized shared branded email chrome.
- Email notification capability version advanced to 1.2.

## Verification

- Business preview test rejects the old generic placeholder and checks actual Request-received copy.
- Persian business preview test checks localized shared footer text.
- Shared content-builder tests cover production/preview copy construction.
