# Catalogue audit

Run this after university/program imports to verify the **persisted Catalogue v3
database**. The command is read-only and never repairs or deletes data.

```bash
uv run --env-file .env python manage.py audit_catalogue
```

Write machine-readable reports as well:

```bash
uv run --env-file .env python manage.py audit_catalogue \
  --json-output var/catalogue-audit.json \
  --csv-output var/catalogue-audit.csv
```

For CI/operator gates, add `--fail-on-errors`. Without that flag the command exits
normally even when it reports ERROR findings, which makes first-pass investigation
safe.

## Severity

- **ERROR**: broken catalogue invariant or an active offering that is not ready for
  Application creation (for example, no active amount-bearing tuition).
- **WARNING**: suspicious/incomplete data that can still be legitimate when the
  source did not provide it (for example, a missing translation or graduate thesis
  type).
- **INFO**: notable but valid state, currently including numeric Program slug tails.

The audit checks university public-data completeness, Program localized identity,
structured instruction languages, active offerings, Intake/source ownership,
structured fees, possible duplicate identities, public notes for likely provenance
leakage, unused active academic units, and Application tuition readiness.

Review findings before changing data. Do not "fix" source-unknown values merely to
make the report empty; warnings intentionally distinguish incomplete source data
from invalid data.
