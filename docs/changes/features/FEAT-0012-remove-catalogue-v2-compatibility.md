# FEAT-0012 — Remove Catalogue v2 compatibility

Status: IMPLEMENTED

## Request

Complete the Catalogue v3 transition by removing the Catalogue v2 compatibility
model/fields and all remaining runtime dependencies.

## Result

- Removed `Semester`, legacy Program language/duration fields, and fixed
  ProgramOffering pricing/currency/basis fields.
- Application creation now snapshots canonical structured tuition/deposit fees.
- Normalized JSON import schema v2 uses `intake` plus explicit structured `fees`.
- Rasa imports now create Intake and OfferingFee rows directly.
- Admin and catalogue dump expose only Catalogue v3.
- Removed `backfill_catalogue_v2` and the obsolete Catalogue-v2 test module.
- Added v3-only regression guards and updated SDD traceability/documentation.

## Verification

Repository Python sources compile successfully. Full `make check` could not be
executed in the delivery environment because `uv` could not reach PyPI to install
locked dependencies; run `make check` in the normal development environment.
