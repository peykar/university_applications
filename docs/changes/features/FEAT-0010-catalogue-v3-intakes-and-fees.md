# FEAT-0010 — Catalogue v3 intakes and structured fees

Catalogue v3 generalizes ProgramOffering from semester-shaped and fixed-column pricing to canonical Intake + OfferingFee data. This follows supplied university tuition sheets where “Academic Intake” is not a semester and where “Advance Payment Fee” and language-specific foundation tuition cannot be represented faithfully by one cash/preparatory column.

Compatibility fields remain temporarily to avoid breaking existing Applications, filters, API consumers and imported rows. New normalized imports create Intake and OfferingFee rows. Legacy JSON `semester` and fixed fee fields remain accepted during the transition.

## Admin presentation follow-up

Catalogue v3 structured fees are now the primary pricing presentation in Django
Admin. Program pages show a structured fee summary for each offering and point
staff to the offering change page for row-level editing. The ProgramOffering
change page exposes OfferingFee rows inline, and OfferingFee also has its own
admin list/edit view. Legacy Semester and fixed price columns remain available
only in a collapsed **Legacy compatibility pricing** section while older
consumers are migrated.

