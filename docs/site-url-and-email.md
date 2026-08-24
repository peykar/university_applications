# Site URL and Email Configuration

## Canonical public URL

TurkDemy defines one canonical public URL:

```dotenv
SITE_URL=https://turkdemy.com
```

This is different from `DJANGO_ALLOWED_HOSTS`.

`SITE_URL` answers:

> What absolute public URL should TurkDemy place in emails, notifications,
> background jobs, exports, and other generated links?

Examples:

```text
https://turkdemy.com/en/programs/computer-engineering/
https://turkdemy.com/en/dashboard/
```

Do not hard-code `turkdemy.com` in application code.

If the domain later changes, update `SITE_URL` and the related environment
variables.

## Absolute URL helper

Use:

```python
from apps.core.urls import absolute_url

url = absolute_url(
    "program-detail",
    slug,
    language="en",
)
```

For a relative path that is already known:

```python
from apps.core.urls import absolute_path

url = absolute_path("/en/dashboard/")
```

## Related environment variables

```dotenv
SITE_URL=https://turkdemy.com

DJANGO_ALLOWED_HOSTS=turkdemy.com,www.turkdemy.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://turkdemy.com,https://www.turkdemy.com

CORS_ALLOWED_ORIGINS=https://turkdemy.com
```

These settings have different purposes:

- `SITE_URL` — canonical outbound/public URL
- `DJANGO_ALLOWED_HOSTS` — accepted HTTP `Host` headers
- `DJANGO_CSRF_TRUSTED_ORIGINS` — trusted browser origins for CSRF
- `CORS_ALLOWED_ORIGINS` — cross-origin browser clients allowed to access APIs

## Email configuration

All SMTP configuration is environment-driven.

Example production configuration:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...

DEFAULT_FROM_EMAIL=TurkDemy <noreply@turkdemy.com>
SERVER_EMAIL=TurkDemy <noreply@turkdemy.com>
SUPPORT_EMAIL=support@turkdemy.com
```

Local development defaults to Django's console email backend, so messages are
printed in the terminal instead of being delivered.

## Email helper

Use the shared helper:

```python
from apps.core.services.emailing import send_email

send_email(
    subject="Your TurkDemy application",
    to="student@example.com",
    text_body="Your application has been updated.",
)
```

Application-specific email services should build their links with
`absolute_url()` and then call `send_email()`.

## Design rule

Domain names, absolute public URLs, sender/support email addresses, and SMTP
credentials must not be hard-coded in application/business logic.
