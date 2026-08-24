# Authentication

TurkDemy uses `django-allauth` for Google, Telegram, and passwordless email
authentication. All methods resolve to the same `accounts.User`.

Authentication endpoints are intentionally outside the language-prefixed URL
tree so external callback URLs remain stable:

```text
/accounts/login/
/accounts/signup/
/accounts/google/login/callback/
/accounts/telegram/login/callback/
```

## Email code login

Email signup/login is passwordless. Login codes and email-verification codes
expire after 10 minutes, allow up to 5 attempts, and support resending.

## Google

Configure:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

Production callback:

```text
https://turkdemy.com/accounts/google/login/callback/
```

Local callback:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

Google verified-email authentication may connect to an existing TurkDemy
account with the same email.

## Telegram

Configure:

```env
TELEGRAM_BOT_ID=123456789
TELEGRAM_BOT_TOKEN=123456789:complete-token
TELEGRAM_AUTH_DATE_VALIDITY=30
```

The complete BotFather token is required. Telegram does not provide email, so
email is not globally required for social signup. django-allauth's
`SocialAccount.uid` is canonical; TurkDemy also mirrors Telegram UID/username
onto the existing User fields.

## Install and migrate

```bash
uv lock
uv sync --all-groups
uv run python manage.py migrate
uv run pre-commit run --all-files
make check
```

Provider buttons are only displayed when their credentials are configured.

## Reverse proxy and HTTPS callbacks

TurkDemy trusts Nginx's forwarded HTTPS scheme:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
```

The production Nginx site should forward:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
```

This makes django-allauth generate the public HTTPS callback URL instead of
an internal `http://` URL when Django is behind Nginx.
