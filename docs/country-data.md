# Country Reference Data

Country identity and ISO codes come from `pycountry` (ISO 3166-1). Localized display names come from Unicode CLDR through `Babel`.

## Populate countries

```bash
uv run python manage.py populate_countries
```

The command is idempotent and uses `Country.iso2` as the stable external key. It fills ISO2, ISO3, English/Persian/Turkish/Arabic names, localized slugs, and `is_active`.

To mark database countries inactive when no longer present in the current ISO dataset:

```bash
uv run python manage.py populate_countries --deactivate-missing
```

Rows are deactivated rather than deleted to protect foreign-key references.

The project intentionally does not populate every city worldwide; `Student.city_of_residence` remains free text.

## Audit fields

`populate_countries` uses the configured system audit user for created/updated
reference records.
