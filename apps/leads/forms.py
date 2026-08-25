from __future__ import annotations

from typing import ClassVar, cast

from django import forms

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


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
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


class LeadPreferenceForm(forms.ModelForm):
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
                    "data-placeholder": "Search languages",
                }
            ),
            "preferred_cities": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": "Search cities",
                }
            ),
            "preferred_universities": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": "Search universities",
                }
            ),
            "preferred_departments": forms.SelectMultiple(
                attrs={
                    "class": "searchable-multiselect",
                    "data-placeholder": "Search study fields",
                }
            ),
            "requires_dormitory": forms.Select(
                choices=(
                    ("", "No preference"),
                    ("true", "Required"),
                    ("false", "Not required"),
                )
            ),
            "requires_erasmus": forms.Select(
                choices=(
                    ("", "No preference"),
                    ("true", "Required"),
                    ("false", "Not required"),
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


class LeadDocumentForm(forms.ModelForm):
    class Meta:
        model = LeadDocument
        fields = ("document_type", "name", "file", "description")


class LeadMessageForm(forms.Form):
    body = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Write a message…",
            }
        ),
    )
    attachment = forms.FileField(required=False)

    def clean(self):
        cleaned = super().clean() or {}
        if not cleaned.get("body") and not cleaned.get("attachment"):
            raise forms.ValidationError("Write a message or attach a file.")
        return cleaned


class ApplyProgramForm(forms.Form):
    lead = forms.ModelChoiceField(queryset=Lead.objects.none())
    offering = forms.ModelChoiceField(
        queryset=ProgramOffering.objects.none(),
        required=False,
        empty_label="Any intake / decide later",
    )

    def __init__(self, *args, user, program, **kwargs):
        super().__init__(*args, **kwargs)
        lead_field = cast(forms.ModelChoiceField, self.fields["lead"])
        offering_field = cast(forms.ModelChoiceField, self.fields["offering"])
        lead_field.queryset = Lead.objects.filter(user=user).order_by("-updated_at")
        offering_field.queryset = ProgramOffering.objects.filter(
            program=program,
            is_active=True,
        ).select_related("academic_year", "semester")
