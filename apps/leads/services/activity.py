from __future__ import annotations

from django import forms

from apps.leads.models import Lead, LeadActivity, LeadActivityType


def audit_form_value(field: forms.Field, value) -> str:
    """Normalize a form value into a stable, human-readable audit value."""
    if value in (None, ""):
        return "—"

    if isinstance(field, forms.ModelChoiceField):
        if hasattr(value, "_meta"):
            return str(value)

        queryset = field.queryset
        if queryset is None:
            return str(value)

        try:
            return str(queryset.get(pk=value))
        except (queryset.model.DoesNotExist, ValueError, TypeError):
            return str(value)

    if isinstance(field, forms.ChoiceField):
        value_text = str(value)
        # Django normalizes callable/mapping/Choices inputs when the field is
        # constructed; the widget exposes the concrete iterable used to render
        # the choices.
        for choice_value, label in field.widget.choices:
            if str(choice_value) == value_text:
                return str(label)

    if isinstance(field, forms.BooleanField):
        return "Yes" if bool(value) else "No"

    if hasattr(value, "isoformat") and not isinstance(value, str):
        return str(value.isoformat())

    return str(value)


def form_changes(form: forms.BaseForm) -> list[dict[str, str]]:
    """Return only meaningful changed fields in audit-friendly form."""
    changes: list[dict[str, str]] = []

    for field_name in form.changed_data:
        field = form.fields[field_name]
        old_value = audit_form_value(field, form.initial.get(field_name))
        new_value = audit_form_value(field, form.cleaned_data.get(field_name))
        if old_value == new_value:
            continue

        changes.append(
            {
                "field": field_name,
                "label": str(field.label),
                "old": old_value,
                "new": new_value,
            }
        )

    return changes


def record_applicant_profile_update(
    *,
    lead: Lead,
    form: forms.BaseForm,
    actor,
) -> bool:
    """
    Record a structured applicant-profile audit event.

    Both customer and Agent edit paths call this function so profile changes
    use the same normalization and metadata shape. Returns True when an
    activity was created and False when the submitted form produced no
    meaningful changes.
    """
    changes = form_changes(form)
    if not changes:
        return False

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.APPLICANT_UPDATED,
        description="",
        metadata={"changes": changes},
        is_customer_visible=False,
        created_by=actor,
        updated_by=actor,
    )
    return True
