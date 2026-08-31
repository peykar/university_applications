# CHG-0008 — Program slug rebuild conflict reporting and skip

Status: SUPERSEDED BY CHG-0009
Classification: CHANGE
Owning capability: catalogue
Requirement: CAT-050

## Request and motivation

Canonical structured Program data can legitimately collapse two existing catalogue
records to the same target public slug. The maintenance command must not invent a
synthetic suffix and a single collision must not block unrelated slug maintenance.

## Approved behavior

`rebuild_program_slugs` computes all canonical localized targets before writing. For
each target slug owned by two or more Programs, it reports the locale, conflicting slug,
and every Program ID. Every Program participating in any collision is skipped entirely,
so no subset of its localized slugs is rewritten. Non-conflicting Programs continue to
be updated normally. `--dry-run` uses the same conflict detection and reporting without
writing.

The command does not append numeric, UUID, hash, or source-derived suffixes. Conflicts
remain visible for explicit catalogue review.

## Verification

`RebuildProgramSlugsCommandTests` verifies that a canonical collision is reported, both
conflicting Programs remain unchanged, and a separate non-conflicting Program is still
rebuilt in the same command invocation. Repository verification remains `make format`
followed by `make check`.
