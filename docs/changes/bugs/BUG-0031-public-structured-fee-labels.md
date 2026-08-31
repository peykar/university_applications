# BUG-0031 — Public structured fee labels are lost or duplicated

Status: DONE
Classification: BUG
Owning capability: Catalogue
Requirements: CAT-013, CAT-037, CAT-038, CAT-043

## Report

On a Program detail offering containing list tuition, discounted/scholarship
tuition, advance-payment tuition and deposit, `display_tuition_fee` correctly
selected the discounted tuition as the headline amount but the template rendered
only its amount and basis. This made a scholarship price look like an unlabeled
annual tuition. Other fee rows appended `percentage` directly after the amount,
which could both run into the currency text and duplicate percentages already
present in source labels such as `Advance payment (15%)`.

## Expected behavior

Structured fee semantics must remain distinguishable in public presentation.
The promoted tuition must retain its source/canonical label, structured
percentage must be visible exactly once, and every amount-bearing fee must show
its fee basis without guessing relationships between fee rows.

## Reproduction

Create one active offering with:

- list tuition: USD 5,550 annual, label `Tuition fee`;
- discounted tuition: USD 4,995 annual, 10%, label `Scholarship fee (10%)`;
- advance payment: USD 4,246 annual, 15%, label `Advance payment (15%)`;
- deposit: USD 1,000 one-time, label `Deposit payment`.

Before this fix the headline rendered only `$4,995 USD` + `Annual`, while the
advance-payment fact could render `$4,246 USD15%`.

## Implementation

- Added `OfferingFee.display_label`, preserving the source label and appending a
  structured percentage only when the label does not already contain `%`.
- Updated `templates/public/program_detail.html` so the promoted tuition keeps
  its label and every amount-bearing fee displays its basis.
- Updated fee presentation CSS for label and basis metadata.
- Added rendered-route regression coverage using the four-fee scenario above.

No schema or migration change is required.

## Verification

Covered by `tests/test_catalogue_v3_ui.py::PublicStructuredFeePresentationTests`.
Repository checks are recorded in the delivery response.
