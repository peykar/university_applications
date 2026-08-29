from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write a message…"}),
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "chat-attachment-input"}),
    )

    def clean(self):
        cleaned = super().clean() or {}
        if not cleaned.get("body") and not cleaned.get("attachment"):
            raise forms.ValidationError("Write a message or attach a file.")
        return cleaned
