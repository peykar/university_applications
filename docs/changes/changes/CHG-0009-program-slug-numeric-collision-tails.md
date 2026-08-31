# CHG-0009 — Program slug deterministic numeric collision tails

Status: DONE
Classification: CHANGE
Owning capability: catalogue
Requirement: CAT-050

## Request and motivation

Distinct Program records can legitimately collapse to the same structured public slug.
Rather than skip those records, the operator wants the rebuild to preserve readable URLs
by appending a short numeric tail only where a collision requires disambiguation.

## Approved behavior

`rebuild_program_slugs` computes all canonical localized targets before writing. For a
collision, Programs are ordered by stable Program ID. The first keeps the unsuffixed
canonical slug; subsequent Programs receive the smallest available numeric tail starting
at `-2`. Candidate tails that collide with another canonical or already assigned target
are skipped. The command reports the conflicting locale/base slug and every resolved
Program slug. `--dry-run` produces the same deterministic plan without writes.

The command does not add UUID, hash, or source-specific suffixes. A two-phase write
clears only changing slug fields before final assignment so existing uniqueness
constraints cannot block deterministic swaps within the atomic transaction.

## Verification

`RebuildProgramSlugsCommandTests` covers deterministic numeric collision resolution while
a non-conflicting Program is rebuilt in the same run. Repository verification remains
`make format` followed by `make check`.
