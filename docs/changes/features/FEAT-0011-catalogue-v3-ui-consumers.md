# FEAT-0011 — Catalogue v3 UI consumers

## Problem
Catalogue v3 introduced canonical `Intake` and normalized `OfferingFee`, but several
public/customer/agent/Application presentation paths still read the Catalogue v2
compatibility fields (`Semester`, `tuition`, `tuition_discounted`, `tuition_cash`,
and `preparatory_tuition`). This made the UI dependent on duplicate legacy data.

## Change
- Public programme filters now expose/filter canonical Intake.
- Public programme list/card minimum tuition annotations come from active structured
  tuition/discounted-tuition `OfferingFee` rows.
- Programme detail displays canonical Intake and structured fees.
- Customer Request/Application and agent/student offering labels use Intake.
- Customer programme prices use the canonical structured display tuition fee.
- Application admin uses Intake.
- ProgramOffering API output exposes Intake plus structured fees and no longer exposes
  legacy fixed pricing/Semester fields.
- Legacy model/import fields remain compatibility bridges only.

## Compatibility
Database compatibility fields are intentionally retained for existing data/import
transition. This feature removes them from current presentation consumers; it does
not delete columns or perform a destructive migration.
