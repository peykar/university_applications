from __future__ import annotations

from typing import ClassVar, cast

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.forms import LocalizedFormMixin
from apps.geography.models import City
from apps.universities.models import (
    DegreeType,
    Department,
    ProgramLanguage,
    ProgramOffering,
    University,
    UniversityType,
)

from .models import Lead, LeadDocument, LeadPreference


def _unique_ids_by_label(rows):
    """Keep the first model id for each normalized display label."""
    seen: set[str] = set()
    unique_ids = []
    for object_id, label in rows:
        normalized = (label or "").strip().casefold()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_ids.append(object_id)
    return unique_ids


class LeadForm(LocalizedFormMixin, forms.ModelForm):
    applicant_for = forms.ChoiceField(
        choices=(("self", _("Myself")), ("other", _("Someone else"))),
        initial="self",
        required=False,
        widget=forms.RadioSelect,
        label=_("Who are you applying for?"),
    )

    class Meta:
        model = Lead
        fields: ClassVar[tuple[str, ...]] = (
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "cell",
            "birthdate",
            "gender",
            "nationality",
            "country_of_birth",
            "country_of_residence",
            "city_of_residence",
            "address",
            "passport_no",
            "passport_issuing_authority",
            "passport_date_of_issue",
            "passport_date_of_expiry",
            "english_test_type",
            "english_language_test_score",
            "high_school_gpa",
            "high_school_gpa_scale",
            "educational_background",
            "needs_program_recommendation",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
            "passport_date_of_issue": forms.DateInput(attrs={"type": "date"}),
            "passport_date_of_expiry": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "educational_background": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lead intake is intentionally permissive. Staff can collect and
        # validate missing information after the applicant expresses interest.
        for field_name, field in self.fields.items():
            if field_name != "applicant_for":
                field.required = False


class CustomerLeadEditForm(LeadForm):
    """Customer-facing profile editor without internal workflow controls."""

    class Meta(LeadForm.Meta):
        fields = tuple(
            field_name
            for field_name in LeadForm.Meta.fields
            if field_name != "needs_program_recommendation"
        )


class LeadPreferenceForm(LocalizedFormMixin, forms.ModelForm):
    preferred_degrees = forms.MultipleChoiceField(
        choices=DegreeType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    preferred_university_types = forms.MultipleChoiceField(
        choices=UniversityType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = LeadPreference
        fields = (
            "tuition_min",
            "tuition_max",
            "tuition_currency",
            "preferred_degrees",
            "preferred_languages",
            "preferred_cities",
            "preferred_universities",
            "preferred_departments",
            "preferred_university_types",
            "requires_dormitory",
            "requires_erasmus",
            "notes",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "preferred_languages": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": _("Search languages"),
                    "data-empty-label": _("No matching options"),
                    "data-remove-label": _("Remove"),
                }
            ),
            "preferred_cities": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": _("Search cities"),
                    "data-empty-label": _("No matching options"),
                    "data-remove-label": _("Remove"),
                }
            ),
            "preferred_universities": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": _("Search universities"),
                    "data-empty-label": _("No matching options"),
                    "data-remove-label": _("Remove"),
                }
            ),
            "preferred_departments": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": _("Search study fields"),
                    "data-empty-label": _("No matching options"),
                    "data-remove-label": _("Remove"),
                }
            ),
            "requires_dormitory": forms.Select(
                choices=(
                    ("", _("No preference")),
                    ("true", _("Required")),
                    ("false", _("Not required")),
                )
            ),
            "requires_erasmus": forms.Select(
                choices=(
                    ("", _("No preference")),
                    ("true", _("Required")),
                    ("false", _("Not required")),
                )
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        preferred_languages_field = cast(
            forms.ModelMultipleChoiceField, self.fields["preferred_languages"]
        )
        preferred_languages_field.queryset = ProgramLanguage.objects.filter(
            is_active=True
        ).order_by("name_en")
        preferred_cities_field = cast(
            forms.ModelMultipleChoiceField, self.fields["preferred_cities"]
        )
        preferred_cities_field.queryset = City.objects.filter(is_active=True).order_by("name_en")
        preferred_universities_field = cast(
            forms.ModelMultipleChoiceField, self.fields["preferred_universities"]
        )
        preferred_universities_field.queryset = University.objects.filter(is_active=True).order_by(
            "name_en"
        )
        preferred_departments_field = cast(
            forms.ModelMultipleChoiceField, self.fields["preferred_departments"]
        )
        department_rows = (
            Department.objects.filter(is_active=True)
            .values_list("pk", "name_en")
            .order_by("name_en", "pk")
        )
        canonical_department_ids = _unique_ids_by_label(department_rows)
        preferred_departments_field.queryset = Department.objects.filter(
            pk__in=canonical_department_ids
        ).order_by("name_en")

        if self.instance and self.instance.pk:
            self.initial["preferred_degrees"] = self.instance.preferred_degrees
            self.initial["preferred_university_types"] = self.instance.preferred_university_types

            canonical_departments_by_name = {
                (name or "").strip().casefold(): object_id
                for object_id, name in preferred_departments_field.queryset.values_list(
                    "pk", "name_en"
                )
            }
            self.initial["preferred_departments"] = [
                canonical_departments_by_name[normalized]
                for name in self.instance.preferred_departments.values_list("name_en", flat=True)
                if (normalized := (name or "").strip().casefold()) in canonical_departments_by_name
            ]

    def clean_requires_dormitory(self):
        value = self.data.get("requires_dormitory", "")
        if value == "":
            return None
        return value == "true"

    def clean_requires_erasmus(self):
        value = self.data.get("requires_erasmus", "")
        if value == "":
            return None
        return value == "true"


class LeadDocumentForm(LocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = LeadDocument
        fields = ("document_type", "file", "description")


class LeadDocumentReplacementForm(LocalizedFormMixin, forms.Form):
    file = forms.FileField(label=_("Replacement file"))


class ApplyProgramForm(LocalizedFormMixin, forms.Form):
    applicant = forms.ChoiceField(
        choices=(),
        widget=forms.RadioSelect,
        label=_("I am applying for"),
    )
    offering = forms.ModelChoiceField(
        queryset=ProgramOffering.objects.none(),
        required=False,
        empty_label=_("Any intake / decide later"),
        label=_("When would you like to start?"),
    )
    new_first_name = forms.CharField(
        required=False,
        label=_("First name"),
    )
    new_last_name = forms.CharField(
        required=False,
        label=_("Last name"),
    )
    new_email = forms.EmailField(
        required=False,
        label=_("Email"),
    )
    new_cell = forms.CharField(
        required=False,
        label=_("Phone"),
    )

    def __init__(self, *args, user, program, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.program = program

        leads = list(Lead.objects.filter(user=user).order_by("-updated_at"))
        user_email = (user.email or "").strip().casefold()
        self_lead = next(
            (
                lead
                for lead in leads
                if user_email and (lead.email or "").strip().casefold() == user_email
            ),
            None,
        )

        choices: list[tuple[str, str]] = []
        self.applicant_options: list[dict[str, object]] = []

        if self_lead is None:
            choices.append(("self_new", str(_("Myself"))))
            self.applicant_options.append(
                {
                    "value": "self_new",
                    "title": str(_("Myself")),
                    "subtitle": str(_("Use the details we already know about your account.")),
                    "is_self": True,
                    "is_new": True,
                }
            )

        for lead in leads:
            is_self = self_lead is not None and lead.pk == self_lead.pk
            title = str(_("Myself")) if is_self else str(lead) or str(_("Applicant"))
            subtitle = (
                str(lead)
                if is_self and str(lead)
                else (lead.email or str(_("Applicant managed by you")))
            )
            value = f"lead:{lead.pk}"
            choices.append((value, title))
            self.applicant_options.append(
                {
                    "value": value,
                    "title": title,
                    "subtitle": subtitle,
                    "is_self": is_self,
                    "is_new": False,
                }
            )

        choices.append(("new", str(_("Someone new"))))
        self.applicant_options.append(
            {
                "value": "new",
                "title": str(_("Someone new")),
                "subtitle": str(_("Create an applicant for another person.")),
                "is_self": False,
                "is_new": True,
            }
        )

        applicant_field = cast(forms.ChoiceField, self.fields["applicant"])
        applicant_field.choices = choices

        if not self.is_bound:
            applicant_field.initial = choices[0][0]
            self.fields["new_first_name"].initial = user.first_name or ""
            self.fields["new_last_name"].initial = user.last_name or ""
            self.fields["new_email"].initial = user.email or ""
            self.fields["new_cell"].initial = getattr(user, "cell", "") or ""

        offering_field = cast(forms.ModelChoiceField, self.fields["offering"])
        offering_field.queryset = ProgramOffering.objects.filter(
            program=program,
            is_active=True,
        ).select_related("academic_year", "intake")

    def clean(self):
        cleaned = super().clean() or {}
        applicant = cleaned.get("applicant")

        if isinstance(applicant, str) and applicant.startswith("lead:"):
            lead_id = applicant.removeprefix("lead:")
            lead = Lead.objects.filter(
                pk=lead_id,
                user=self.user,
            ).first()
            if lead is None:
                self.add_error("applicant", _("Choose a valid applicant."))
            else:
                cleaned["selected_lead"] = lead
        elif applicant not in {"self_new", "new"}:
            self.add_error("applicant", _("Choose who is applying."))

        return cleaned
