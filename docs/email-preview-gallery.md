# Email Preview Gallery

The superuser-only Email Preview Gallery lives at:

`/admin-tools/email-previews/`

It is the canonical registry for outgoing TurkDemy email.

## What it provides

- One registered entry for every outgoing account email type.
- Preview links for every language in `settings.LANGUAGES`.
- Real rendering through `TurkDemyAccountAdapter`, using safe sample data.
- HTML email preview and plain-text fallback.
- A "Send test to myself" action that sends only to the logged-in superuser.
- A warning when a non-English preview renders identically to English.

No real applicant/customer data is used in previews.

## Adding a new outgoing email

Every new outgoing email **must** be added to `EMAIL_PREVIEW_REGISTRY`.

For django-allauth account emails, a Django system check scans the installed
allauth package for `account/email/*_subject.txt`. If a new allauth email exists
without a registry entry, `manage.py check` fails with `turkdemy.E001`.

Project-specific email sent through `apps.core.services.emailing.send_email`
must also supply an `email_type` registered in `EMAIL_PREVIEW_REGISTRY`; an
unregistered type raises `ValueError`.

This makes the preview gallery part of the email feature contract rather than
optional documentation.

## Preview rendering

HTML previews are served by a dedicated superuser-only endpoint and displayed in
an isolated iframe. The gallery does not inject full email documents through
`srcdoc`, avoiding browser parsing/escaping problems with large HTML emails.

The preview renderer validates that every email has a non-empty subject,
plain-text body and HTML body. Regression tests render every registered email
for every language in `settings.LANGUAGES`. If rendering fails, the preview
page shows an explicit error instead of an empty preview frame.

### Request-context regression coverage

The exhaustive preview test renders each registered email through the
superuser-only HTML preview endpoint rather than calling the allauth adapter
directly. django-allauth email rendering relies on its active request context
for site/domain formatting, so endpoint-level testing mirrors production
behavior and catches both rendering and routing failures.
