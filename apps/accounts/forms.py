from __future__ import annotations

from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.core.forms import LocalizedFormMixin

User = get_user_model()


class AddLoginEmailForm(LocalizedFormMixin, forms.Form):
    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "you@example.com",
            }
        ),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()

        if EmailAddress.objects.filter(email__iexact=email).exclude(user=self.user).exists():
            raise forms.ValidationError(
                _("This email address is already connected to another TurkDemy account.")
            )

        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(
                _("This email address already belongs to another TurkDemy account.")
            )

        return email
