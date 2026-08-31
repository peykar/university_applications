from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms import LocalizedFormMixin


class MessageForm(LocalizedFormMixin, forms.Form):
    body = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": _("Write a message…")}),
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "chat-attachment-input"}),
    )

    def clean(self):
        cleaned = super().clean() or {}
        if not cleaned.get("body") and not cleaned.get("attachment"):
            raise forms.ValidationError(_("Write a message or attach a file."))
        return cleaned
