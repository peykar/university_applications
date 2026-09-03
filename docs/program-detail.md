# Program Detail Page

The program detail page is designed as a decision page rather than a raw model
view.

## Program information

It shows:
- degree
- instruction language composition (including percentages when known)
- academic unit and field/department
- structured study mode
- fraction-safe duration
- thesis type when applicable
- program description

## Offerings

Active ProgramOffering records are rendered as cards with:
- academic year
- semester/intake
- standard tuition
- discounted tuition and discount percentage
- cash tuition
- installment tuition
- deposit
- preparatory tuition when supplied
- whether preparation is included
- fee basis
- quota
- application deadline
- open/closed indication based on the deadline
- commercial/source notes when supplied

## University context

The page also exposes the parent university:
- logo
- banner
- city and type
- YÖK / MOE / MOH indicators
- Erasmus+
- dormitory availability
- active program count
- university description
- gallery/media
- university website

## Related discovery

Two related-program sections are shown:

1. **Similar programs** across the catalogue, ranked by a similarity score that
   favors matching department, degree and language.
2. **More programs at this university**.

Similar-program cards present the lowest active tuition in customer-facing copy as **“Tuition from <amount>”** when available; internal/query terminology such as “minimum active tuition” is not exposed to customers.

## Internal catalogue notes

`Program.internal_notes` is operational staff/import context and must never be
rendered on the public Program Detail page. Public descriptive copy continues to
come from the localized `description_*` fields.

## Catalogue v3 offering presentation
Programme offering cards use canonical `Intake` and active structured `OfferingFee`
rows. The primary displayed tuition prefers an active discounted-tuition fee when
present, otherwise list tuition; other structured fees are shown with their source
label, language (when applicable), amount/percentage, and basis. Catalogue pricing
is sourced only from canonical Intake and structured OfferingFee data.

## Structured fee presentation

The offering headline uses the canonical payable tuition selection (discounted
structured tuition when available, otherwise list tuition), but it must retain
that `OfferingFee`'s source/canonical label. This prevents a scholarship or other
discounted price from appearing as an unlabeled generic tuition amount.

Structured percentages are displayed exactly once: a source label containing a
percent sign is preserved as-is; otherwise the structured percentage is appended
to the display label. Every amount-bearing fee also displays its canonical fee
basis (annual, per semester, whole program, per credit, or one time). Public UI
does not calculate or infer discounts between fee rows.

## Conversion layout (UI-0011)

Program Detail uses a decision-oriented two-column desktop layout: the main column contains
offerings and supporting catalogue context while a prominent **Start a Request** card remains
sticky beside it. A lone active Offering expands across the main column rather than reserving
space for a nonexistent second card. University media/context is intentionally compact so the
page maintains useful information density.

At tablet and mobile widths the conversion card is moved before the long detail stream. Tablet
uses a compact action treatment where space permits; mobile returns to a single-column card with
full-width actions. This is presentation-only: Request workflow semantics and Program SEO identity
remain unchanged.

On narrow mobile screens, University facts stay in a compact two-column grid, the University
description is collapsed behind a localized read-more control, and University media spans the
available content width. Similar Programs becomes a horizontally swipeable snap row rather than a
long vertical stack. The compact list for additional programs at the same University remains
vertical because it is intentionally scan-oriented.


### Mobile duplication guard

On phone-sized viewports the Program hero keeps extra safe spacing from the mobile shell. The
University mini-card and standalone four-item summary strip are not rendered visually at this
breakpoint because their facts are already exposed by the hero and later University showcase. This
keeps the mobile reading sequence concise while preserving the full desktop/tablet decision layout.
