# UI-0011 — Program Detail conversion layout

Status: IMPLEMENTED
Requested: 2026-09-03

## Request

Improve the public Program Detail page after CHG-0023 so the Request conversion action,
offering information, University context and related discovery use the available page space
more deliberately, especially in RTL, without changing catalogue or Request behavior.

## Classification check

UI only. No Program, Offering, Request, authentication, reopen, pricing, SEO identity,
permissions or persistence behavior changes.

## Decision

- Keep the existing desktop main-content + sticky conversion-sidebar architecture, but
  increase the sidebar to 320px and reduce excess spacing between major sections.
- Give the **Start a Request** card stronger visual hierarchy and a larger primary action.
- Let a single active Offering use the full main-content width instead of leaving an empty
  second card column.
- Compact the University showcase/media block and related cards without removing content.
- Below desktop width, move the Request card before the long content stream; use a compact
  horizontal action treatment on tablet and a single-column action stack on mobile.
- Preserve logical/RTL layout behavior and all CHG-0023 canonical City/GeneralField links.

## Implementation

- Updated `static/css/turkdemy.css` with a scoped UI-0011 Program Detail layout layer.
- Added structural regression coverage in `tests/test_program_detail_conversion_layout.py`.
- Updated `docs/program-detail.md`, Catalogue SDD and changelog.

## Acceptance

- [x] Desktop Request CTA is visually prominent and remains sticky.
- [x] A single Offering fills the available main-content column.
- [x] Upper-page spacing is materially tighter without removing information.
- [x] University context is more compact.
- [x] Tablet/mobile users encounter the Request action before the long detail content.
- [x] RTL/LTR behavior continues to rely on logical document direction.
- [x] No Request workflow, catalogue data or SEO behavior changes.
