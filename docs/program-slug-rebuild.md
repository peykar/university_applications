# Rebuild Program public slugs

Program public slugs are globally unique and use the localized University prefix.
For an existing database, inspect the planned rewrite first:

```bash
uv run --env-file .env python manage.py rebuild_program_slugs --dry-run
```

Then apply it:

```bash
uv run --env-file .env python manage.py rebuild_program_slugs
```

The command computes the complete target set before writing. If two or more Programs
would receive the same localized slug, it reports the conflicting locale, slug, and
Program IDs, leaves every Program in that collision unchanged, and continues rebuilding
other Programs. A Program involved in a collision in any locale is skipped as a whole.
No numeric, UUID, hash, or source-specific suffix is invented automatically. Run the
command before generating/applying the local Django migration that adds the Program
slug uniqueness constraints.

Example:

```text
nursing-bachelor-turkish
-> istanbul-atlas-university-nursing-bachelor-turkish
```

## Graduate thesis variants

For Programs with `thesis_type`, rebuilding also ensures the program-specific slug
contains `thesis` or `non-thesis`. Example:
`istanbul-atlas-university-business-administration-master-non-thesis-turkish`.
The command is idempotent and replaces a stale opposite thesis marker.

## Canonical structured inputs

The rebuild ignores the existing Program slug as an input. It derives each locale
from the University localized slug, Program localized name, degree, thesis type
when applicable, and structured instruction languages. All languages are included
(primary first), so multilingual variants remain distinguishable.

If an Academic Unit or Department exists but is untranslated in the target locale,
its English slug (or English name as a final fallback) remains in the localized
Program slug. This preserves the structured distinction until translations are filled.
