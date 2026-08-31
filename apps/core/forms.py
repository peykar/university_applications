from __future__ import annotations

from typing import Any

from django.utils.translation import gettext


class LocalizedFormMixin:
    fields: dict[str, Any]

    """Translate generated form presentation strings for the active locale.

    Explicit lazy translations keep working normally. This mixin additionally
    gives model-derived labels/help text and string widget attributes the same
    gettext lookup so translation-enabled pages do not leak generated English
    presentation copy merely because a field label came from model metadata.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._localize_form_presentation()

    def _localize_form_presentation(self) -> None:
        for field in self.fields.values():
            if field.label:
                field.label = gettext(str(field.label))
            if field.help_text:
                field.help_text = gettext(str(field.help_text))

            empty_label = getattr(field, "empty_label", None)
            if empty_label:
                field.empty_label = gettext(str(empty_label))

            for key in (
                "placeholder",
                "title",
                "aria-label",
                "data-placeholder",
                "data-empty-label",
                "data-remove-label",
            ):
                value = field.widget.attrs.get(key)
                if value:
                    field.widget.attrs[key] = gettext(str(value))
