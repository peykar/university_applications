# Model Field Guidelines

## Help text

Model fields whose meaning is not obvious to an administrator, developer, or
internal operator should define Django `help_text`.

This is especially important for:
- acronyms and regulatory terms such as YÖK, MOE, and MOH
- approval/recognition flags
- business-specific status or ranking fields
- pricing concepts whose interpretation is not obvious
- admission-specific fields
- fields where a value may otherwise be misinterpreted

`help_text` should explain the business meaning of the field rather than merely
repeat its name.

Example:

```python
is_yok_recognized = models.BooleanField(
    default=False,
    help_text=_(
        "Whether the university is recognized by YÖK "
        "(the Council of Higher Education of Türkiye)."
    ),
)
```

Help text is part of the model definition so it is automatically available to
Django forms and the Django admin.

When adding or changing a domain-specific model field, review whether it needs
`help_text` as part of the same change.
