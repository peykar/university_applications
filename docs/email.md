# Email design

TurkDemy sends multipart email: a plain-text fallback plus a branded HTML
version.

## Shared template

`templates/emails/base.html` is the shared visual shell for outgoing email.
It provides TurkDemy branding, responsive email-safe table layout, typography,
footer and RTL direction for Persian/Arabic requests.

`TurkDemyAccountAdapter` attaches the shared HTML representation to all
django-allauth account emails that do not already provide a dedicated HTML
template. Application mail sent through `apps.core.services.emailing.send_email`
also receives the shared HTML shell automatically.

Individual emails can provide purpose-specific HTML while extending the same
shell. Login codes use
`templates/account/email/login_code_message.html`, which displays the code as
the primary visual element.

## User-facing codes

Login and email-verification codes use five numeric digits:

```python
{"numeric": True, "dashed": False, "length": 5}
```

This is configured independently through
`ACCOUNT_LOGIN_BY_CODE_FORMAT` and
`ACCOUNT_EMAIL_VERIFICATION_BY_CODE_FORMAT`.
