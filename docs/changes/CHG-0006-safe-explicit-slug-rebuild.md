# CHG-0006 — Safe explicit slug rebuild

Added the SDD-defined `rebuild_slugs` maintenance command for intentional regeneration
of stale stored slugs. It provides dry-run output, scoped collision preflight, atomic
writes, and regenerates through normal model `save()` behavior rather than bulk SQL.
Normal saves remain fill-only.
