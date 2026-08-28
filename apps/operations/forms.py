from typing import ClassVar, cast

from django import forms
from django.utils import timezone

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
        if agent is not None:
            self.instance.agent = agent
        assignee_field = cast(forms.ModelChoiceField, self.fields["assignee"])
        if agent is not None:
            assignee_field.queryset = agent.users.filter(is_active=True).order_by(
                "first_name", "last_name", "email"
            )
        else:
            queryset = assignee_field.queryset
            assert queryset is not None
            assignee_field.queryset = queryset.none()


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
