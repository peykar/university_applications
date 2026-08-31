# Catalogue v3 cutover for an existing database

Catalogue v3 is now the only active catalogue model. The repository intentionally
ships without generated Django migration files, so an existing development or
production database needs one explicit data-preservation step before you generate
and apply the destructive migration that removes Catalogue v2 columns/tables.

## Fresh database

No cutover command is needed. Follow `docs/fresh-database.md`; the migrations you
generate from the current models will contain only the v3 schema.

## Existing database created by an older TurkDemy revision

Back up the database first. After switching the code to this revision, **do not
run `makemigrations`/`migrate` yet**. The old database columns still exist even
though current Django models no longer expose them.

Run a dry run:

```bash
uv run --env-file .env python manage.py prepare_catalogue_v3_cutover --dry-run
```

The command reads legacy columns directly through Django's database connection;
it does not restore the removed Catalogue v2 models. It fills only missing v3
data:

- whole-year Program duration → `duration_months` when canonical duration is empty;
- single Program language → `ProgramInstructionLanguage` only when no canonical
  language rows exist;
- legacy Semester → University/AcademicYear-specific `Intake` only when the
  offering has no Intake;
- fixed legacy prices → `OfferingFee` rows only when the offering has no
  structured fees at all.

If the dry run reports an unresolved offering with no Intake, resolve that data
before continuing. When the dry run is clean, apply the backfill:

```bash
uv run --env-file .env python manage.py prepare_catalogue_v3_cutover
```

Then generate and apply the local migration history:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
make check
```

After the destructive migration has removed the legacy columns, rerunning
`prepare_catalogue_v3_cutover` simply reports that no Catalogue v2 database
columns are present.
