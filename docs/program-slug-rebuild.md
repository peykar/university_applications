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

The command computes the complete target set before writing and aborts if two
Programs would receive the same localized slug. Run it before generating/applying
the local Django migration that adds the Program slug uniqueness constraints.

Example:

```text
nursing-bachelor-turkish
-> istanbul-atlas-university-nursing-bachelor-turkish
```
