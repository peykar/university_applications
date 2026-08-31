# BUG-0029 — Program slug numeric-tail write collision

Status: DONE
Classification: BUG
Owning capability: catalogue
Requirement: CAT-050

## Problem

CHG-0009 correctly planned deterministic numeric tails for canonical Program slug
collisions, but the final write called `Program.save()`. `BaseModel.save()` invokes the
Program canonical slug builder, which removed the planned numeric tail and restored the
conflicting canonical base slug. The database unique constraint then raised
`IntegrityError`.

## Resolution

The rebuild keeps its existing two-phase transactional strategy, first clearing only slug
fields that will change. The second phase now persists the command's fully resolved targets
with a queryset update instead of calling `Program.save()`. This intentionally bypasses
canonical slug regeneration during this one management operation while preserving
`updated_by` and `updated_at` audit metadata.

Normal Program saves continue to use the canonical structured slug builder; the bypass is
limited to the rebuild command after it has already computed and collision-resolved the
canonical targets.

## Verification

Covered by `RebuildProgramSlugsCommandTests`, especially the regression that creates two
Programs with the same canonical slug and expects the deterministic owner ordering to yield
the base slug and `-2` without violating the unique constraint.
