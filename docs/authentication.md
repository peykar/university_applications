# Authentication and Phone Numbers

## Custom User

The project uses:

```python
AUTH_USER_MODEL = "university_applications.User"
```

## Phone validation

Phone numbers are validated with the Python `phonenumbers` package.

The system stores phone values in E.164 form where possible.

Examples:

```text
+31 6 1234 5678  → +31612345678
+90 532 123 45 67 → +905321234567
```

Format validity is not the same as ownership verification.

## Verification state

`User.cell_verified_at` records when ownership of the user's phone number
has been verified.

A valid phone-number format alone must not set this field.

OTP verification can be added as a separate flow.

## Student phone

`Student.cell` is contact information.

It is validated and normalized, but is not automatically treated as an
authentication identity and does not require verification merely because
it is stored.
