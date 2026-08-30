# FEAT-0010 — Catalogue v3 intakes and structured fees

Catalogue v3 generalizes ProgramOffering from semester-shaped and fixed-column pricing to canonical Intake + OfferingFee data. This follows supplied university tuition sheets where “Academic Intake” is not a semester and where “Advance Payment Fee” and language-specific foundation tuition cannot be represented faithfully by one cash/preparatory column.

Compatibility fields remain temporarily to avoid breaking existing Applications, filters, API consumers and imported rows. New normalized imports create Intake and OfferingFee rows. Legacy JSON `semester` and fixed fee fields remain accepted during the transition.
