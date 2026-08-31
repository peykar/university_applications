# BUG-0030 — Program ordinary-save canonical slug collision

Status: DONE
Classification: BUG
Owning capability: catalogue
Requirement: CAT-050

## Problem

CHG-0009 made `rebuild_program_slugs` resolve canonical Program slug collisions with
numeric tails, but ordinary `Program.save()` still regenerated the raw canonical base.
During normalized imports, saving a `ProgramInstructionLanguage` saves its parent Program
after the structured language becomes available. If another Program already owned the
same localized canonical slug, the database unique constraint raised `IntegrityError`
instead of assigning a numeric tail.

## Resolution

Canonical Program generation now resolves each localized base against already persisted
Programs during ordinary saves. The first persisted owner keeps the base; a later owner
receives the smallest available `-2`, `-3`, ... tail. A Program that already owns a valid
tail keeps it on subsequent saves, preventing routine imports/edits from churning public
URLs.

`rebuild_program_slugs` remains the explicit global normalization path: it can reassign
base/tail ownership deterministically by Program ID using its two-phase planner.

## Verification

`UniversityProgramJsonImportTests` covers two imported Programs whose distinct English
identities intentionally collapse to the same Arabic canonical slug. Import must complete
with the base and `-2`, and re-import must remain idempotent with the same two rows/slugs.
