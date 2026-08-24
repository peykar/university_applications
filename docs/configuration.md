# Configuration

TurkDemy reads local environment variables from the project `.env` file via
`python-dotenv`. Environment variables supplied by the process/container can
also be used.

Start from:

```bash
cp .env.example .env
```

## Django

```dotenv
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

## Automated audit/system user

```dotenv
SYSTEM_USER_USERNAME=system
SYSTEM_USER_EMAIL=system@turkdemy.local
SYSTEM_USER_IS_ACTIVE=0
SYSTEM_USER_IS_STAFF=0
SYSTEM_USER_IS_SUPERUSER=0
```

See `docs/auditing.md` for system-user behavior and security constraints.
