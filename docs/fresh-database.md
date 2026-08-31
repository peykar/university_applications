# Fresh database setup

This package intentionally contains no generated Django migrations and no SQLite database.
Legacy Lead-specific messaging models and the legacy-message migration command have been removed.
Messaging uses only `Conversation`, `Message`, `MessageAttachment`, and
`ConversationParticipantState` from `apps.messaging`.

Generate a completely new migration history and database:

```bash
uv sync
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py check
uv run pytest
```

For an **existing** database from a pre-CAT-044 revision, do not use the fresh
setup sequence blindly. Follow [`catalogue-v3-cutover.md`](catalogue-v3-cutover.md)
first so missing Intake/OfferingFee/language/duration data is preserved before
locally generated migrations drop the legacy Catalogue v2 columns/tables.
