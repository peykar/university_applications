# UI-0011 — Program Detail conversion layout

Status: IMPLEMENTED — MOBILE STABILIZATION APPLIED
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

## Mobile stabilization

After visual review on a narrow Persian viewport, UI-0011 was refined without opening a new UI change:

- Shortened the Request-card explanatory copy so the primary CTA appears sooner.
- Kept University facts in a two-column mobile grid instead of a tall single-column stack.
- Added a compact mobile University-description treatment with explicit **Read more / Show less** controls.
- Let University media use the full mobile content width.
- Changed Similar Programs to a horizontally swipeable, scroll-snapped row on mobile so related discovery does not dominate page height.
- Preserved the compact "More programs at this university" list.
- Added FA/TR/AR translations for the new UI copy.

These are presentation-only refinements; Request workflow, catalogue semantics and SEO identity remain unchanged.

## Mobile repetition/readability stabilization

A second Persian mobile review found two remaining presentation issues. The hero text sat too close
to the mobile shell/viewport edge, and the compact University card plus four-item summary strip
immediately repeated information already visible in the hero and later University section. UI-0011
was therefore stabilized again without opening UI-0012:

- Increased mobile hero top/side/bottom padding to preserve a comfortable reading frame below the
  mobile header.
- Hid the hero University mini-card on mobile; the hero already names/links the University and the
  full University showcase remains later on the page.
- Hid the standalone four-item Program summary strip on mobile; degree/language/duration context is
  already present in the hero, avoiding an immediate duplicate block.
- Desktop/tablet structure and all Program, Offering, Request and SEO semantics remain unchanged.
