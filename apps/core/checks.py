from __future__ import annotations

from importlib.resources import files

from django.core.checks import Error, register

from .email_previews import registered_template_prefixes


@register()
def check_email_preview_registry(app_configs, **kwargs):
    email_dir = files("allauth").joinpath("templates/account/email")
    discovered = {
        f"account/email/{item.name.removesuffix('_subject.txt')}"
        for item in email_dir.iterdir()
        if item.name.endswith("_subject.txt")
    }
    missing = discovered - registered_template_prefixes()
    if not missing:
        return []

    return [
        Error(
            "Outgoing allauth emails are missing from the Email Preview Gallery: "
            + ", ".join(sorted(missing)),
            id="turkdemy.E001",
        )
    ]
