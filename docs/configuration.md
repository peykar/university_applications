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

## Public URL and email

```dotenv
SITE_URL=https://turkdemy.com
DJANGO_ALLOWED_HOSTS=turkdemy.com,www.turkdemy.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://turkdemy.com,https://www.turkdemy.com

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=TurkDemy <noreply@turkdemy.com>
SUPPORT_EMAIL=support@turkdemy.com
```

See `docs/site-url-and-email.md`.

## Customer support links

The optional customer-sidebar WhatsApp action is configured through the
environment. Use an international number including country code. Formatting
characters are accepted; the rendered `wa.me` URL uses digits only.

```dotenv
WHATSAPP_NUMBER=31612345678
```

When empty or unset, **Message us on WhatsApp** is not rendered. The template
never contains a hard-coded phone number.

