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

Minimum active tuition is included where available.

## Internal catalogue notes

`Program.internal_notes` is operational staff/import context and must never be
rendered on the public Program Detail page. Public descriptive copy continues to
come from the localized `description_*` fields.
