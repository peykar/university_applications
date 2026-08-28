from typing import ClassVar

from django import forms
from django.utils import timezone

from apps.accounts.models import User

from .models import (
    CommunicationLog,
    Todo,
)


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ("title", "description", "due_date", "assignee")
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, agent=None, **kwargs):
        super().__init__(*args, **kwargs)
        assignee_field = self.fields["assignee"]
        if not isinstance(assignee_field, forms.ModelChoiceField):
            raise TypeError("TodoForm.assignee must be a ModelChoiceField")
        if agent is not None:
            assignee_field.queryset = agent.users.filter(is_active=True).order_by(
                "first_name", "last_name", "email"
            )
        else:
            queryset = assignee_field.queryset
            assignee_field.queryset = (
                queryset.none() if queryset is not None else User.objects.none()
            )


class CommunicationLogForm(forms.ModelForm):
    class Meta:
        model = CommunicationLog
        fields = (
            "occurred_at",
            "channel",
            "counterparty_type",
            "counterparty_name",
            "summary",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "summary": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not self.instance.pk:
            self.initial["occurred_at"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")
