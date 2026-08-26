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

## Social-provider email verification

Regular email authentication remains mandatory-verification:

```python
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
```

Social authentication does not require a second TurkDemy verification step:

```python
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
```

This means Google users are not asked to verify the same Google email again
after Google has authenticated them. Direct email signup/login still uses the
TurkDemy email-code flow. Telegram is unaffected because it normally does not
supply an email address.

## Existing passwords and Google account linking

django-allauth has a security safeguard for social email authentication: when
a trusted provider matches an existing local account whose email has not yet
been recorded as verified by allauth, the local password can be made unusable.

TurkDemy installs `TurkDemySocialAccountAdapter` to handle legacy accounts.
When Google supplies the same **verified** email address, the adapter first
records that email as verified in allauth's `EmailAddress` table. The existing
local password, staff flag, superuser flag, Leads, Students and Applications
remain unchanged.

This applies only to providers explicitly listed as trusted by the adapter
(currently Google). Telegram does not provide an email address and is not used
for email-based account linking.

If a password was already made unusable before this fix, its old hash cannot
be reconstructed. Restore it once with:

```bash
uv run --env-file .env python manage.py changepassword <username>
```

Future Google logins will preserve that restored password.

## Connecting additional sign-in methods

Authenticated users can manage login methods at:

```text
/accounts/settings/sign-in-methods/
```

The page supports:

- connecting Google to the currently logged-in TurkDemy user;
- connecting Telegram to the currently logged-in TurkDemy user;
- adding and verifying an email address for passwordless email-code login;
- choosing a verified primary email;
- removing email addresses;
- disconnecting Google or Telegram.

Social connections use django-allauth's `process="connect"` flow, not the
normal login flow. This guarantees the newly authenticated provider is
attached to the already authenticated TurkDemy `User`.

Google connection requests reauthentication so the customer explicitly chooses
which Google account to attach.

TurkDemy does not silently merge identities that already belong to another
account. Email additions reject an address that belongs to another User or
allauth `EmailAddress`, and django-allauth prevents connecting a social
identity that is already owned by another user.

The UI also prevents the customer from removing their last usable sign-in
method. A usable method is currently counted as:

- a connected SocialAccount;
- a verified allauth EmailAddress;
- or an existing usable Django password.

## Email verification API

Manual email attachment uses django-allauth's `EmailAddress.send_confirmation()`
model API. This is compatible with current django-allauth versions and uses the
configured code-based email verification flow.

## Google verified-email synchronization

When a connected Google identity contains `email_verified=true`, TurkDemy
synchronizes the matching address into django-allauth's `EmailAddress` table as
verified. If the user has no other primary email, that address also becomes
primary. This enables email-code login without asking the customer to verify
the same Google-owned address again.

Existing installations can repair already-connected Google accounts with:

```bash
uv run --env-file .env python manage.py sync_social_emails
```

The synchronization never transfers an email address that already belongs to a
different TurkDemy user.

## Canonical connection-management page

TurkDemy uses one customer-facing page for authentication connections:

```text
/accounts/settings/sign-in-methods/
```

django-allauth's built-in `/accounts/3rdparty/` endpoint is redirected to this
page. The social-account adapter also returns successful `process="connect"`
flows to the same URL.

This prevents django-allauth's default unstyled account-connection page from
appearing after Google/Telegram connections while keeping allauth responsible
for the underlying secure connection workflow.

## Authentication translations

TurkDemy's authentication and Sign-in methods UI includes project-level
translations for Persian (`fa`), Turkish (`tr`) and Arabic (`ar`). The
catalogues live under:

```text
locale/fa/LC_MESSAGES/django.po
locale/tr/LC_MESSAGES/django.po
locale/ar/LC_MESSAGES/django.po
```

Compiled `.mo` files are committed as well, so deployed environments do not
need to run `compilemessages` just to use these translations.

When authentication copy changes, regenerate/extract messages and update all
three catalogues before release.

## RTL support

The root HTML element is language-aware:

```django
<html
    lang="{{ LANGUAGE_CODE }}"
    dir="{% if LANGUAGE_BIDI %}rtl{% else %}ltr{% endif %}"
>
```

Persian and Arabic therefore render RTL, while English and Turkish remain LTR.
Shared CSS uses RTL-aware layout rules so the visual design remains consistent.

Mixed-direction values such as email addresses and Telegram usernames are
wrapped with `bdi dir="ltr"` so they remain readable inside RTL pages.

## Email code login routing

Consumer email sign-in uses django-allauth's login-by-code endpoints:

- `/accounts/login/code/` (`account_request_login_code`) requests a login code.
- `/accounts/login/code/confirm/` (`account_confirm_login_code`) verifies it.
- `/accounts/signup/` is only for creating a new account.

The TurkDemy templates use the named login-code URLs explicitly so an existing
user attempting to sign in cannot accidentally submit through the signup flow.

## Return to the requested page after authentication

Protected actions use Django's standard `next` query parameter. The authentication
chooser must preserve that value when the user continues with email-code, Google,
or Telegram authentication. django-allauth then returns the authenticated user
to the originally requested protected URL. `LOGIN_REDIRECT_URL` is only the
fallback when no `next` destination exists.
