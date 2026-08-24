# Audit Fields and System User

TurkDemy domain models inherit `BaseModel`, which provides:

```text
created_at
updated_at
created_by
updated_by
```

`created_by` and `updated_by` intentionally have no reverse relation on the
User model (`related_name="+"`).

## Interactive/admin changes

Django Admin uses `AuditAdminMixin`:

- on creation, `created_by` is the logged-in staff user
- on every save, `updated_by` is the logged-in staff user
- audit fields are read-only in Admin

Example:

```text
created_by = alice
updated_by = bob
```

means Alice created the record and Bob most recently changed it through the
admin interface.

## Automated/import changes

Management commands do not have an authenticated request user. They use the
configured non-human system user returned by:

```python
apps.core.audit.get_system_user()
```

New automated records receive:

```text
created_by = system user
updated_by = system user
```

When an importer updates an existing record:

```text
created_by = preserved
updated_by = system user
```

This means the audit trail reflects the most recent actor without losing the
original creator.

## Environment configuration

The system identity is configured in `.env`:

```dotenv
SYSTEM_USER_USERNAME=system
SYSTEM_USER_EMAIL=system@turkdemy.local
SYSTEM_USER_IS_ACTIVE=0
SYSTEM_USER_IS_STAFF=0
SYSTEM_USER_IS_SUPERUSER=0
```

The defaults deliberately create a non-login, non-staff, non-superuser
account. Its password is unusable.

The project refuses to reuse a login-capable account as the system user. If
`SYSTEM_USER_USERNAME` already belongs to a user with a usable password,
TurkDemy raises a configuration error rather than silently taking over that
account.

If `SYSTEM_USER_IS_SUPERUSER=1`, `SYSTEM_USER_IS_STAFF` must also be `1`.
There should normally be no reason for the automated audit identity to have
staff or superuser access.

## Ensure the account explicitly

The user is created lazily the first time an audited management command needs
it. It can also be created/validated explicitly:

```bash
uv run python manage.py ensure_system_user
```

## Shared helpers

`apps/core/audit.py` provides:

```text
get_system_user()
audited_get_or_create(...)
audited_update_or_create(...)
```

Use these helpers in management commands instead of raw `get_or_create()` or
`update_or_create()` for `BaseModel` descendants.

### `audited_get_or_create`

If a row already exists, it is not modified and its audit fields remain
unchanged. If a row is created, both audit actor fields are set.

### `audited_update_or_create`

For new rows:

```text
created_by = actor
updated_by = actor
```

For existing rows:

```text
created_by = unchanged
updated_by = actor
```

## TGate comparison

The previous TGate project also uses a dedicated system user for imports.
TGate hard-codes:

```text
username = system
email = system@localhost
```

and forces that account to staff + superuser.

TurkDemy keeps the same useful audit approach but makes the identity and
permissions environment-configurable and defaults to a safer non-privileged
account.
