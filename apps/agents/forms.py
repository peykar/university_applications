from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.leads.models import (
    DocumentType,
    Lead,
    LeadDocument,
    LeadDocumentReviewStatus,
    LeadProgramInterest,
)
from apps.universities.models import Program, ProgramOffering


class DocumentReviewForm(forms.Form):
    review_status = forms.ChoiceField(
        choices=LeadDocumentReviewStatus.choices,
        label=_("Review decision"),
    )
    review_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label=_("Review note"),
    )


class PromoteChatAttachmentForm(forms.Form):
    document_type = forms.ChoiceField(
        choices=DocumentType.choices,
        label=_("Document type"),
    )
    name = forms.CharField(required=False, label=_("Name"))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        label=_("Description"),
    )


class AgentLeadEditForm(forms.ModelForm):
    """Edit provisional applicant data from Agent Workspace."""

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
            "father_name",
            "mother_name",
            "passport_no",
            "passport_issuing_authority",
            "passport_date_of_issue",
            "passport_date_of_expiry",
            "english_test_type",
            "english_language_test_score",
            "high_school_gpa",
            "high_school_gpa_scale",
            "educational_background",
            "notes",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
            "passport_date_of_issue": forms.DateInput(attrs={"type": "date"}),
            "passport_date_of_expiry": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "educational_background": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A Lead remains intentionally permissive until finalization.
        for field in self.fields.values():
            field.required = False


class AgentLeadDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = LeadDocument
        fields = ("document_type", "file", "description")
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "description": forms.Textarea(attrs={"rows": 2})
        }


class AgentProgramSuggestionForm(forms.ModelForm):
    """Create an agent-suggested program interest for a Lead."""

    class Meta:
        model = LeadProgramInterest
        fields = ("program", "program_offering", "suggestion_reason")
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "suggestion_reason": forms.Textarea(attrs={"rows": 2, "class": "compact-note-input"}),
        }
        labels: ClassVar[dict[str, object]] = {
            "suggestion_reason": _("Suggestion note (optional)"),
        }

    def __init__(self, *args, lead=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.lead = lead
        program_field = self.fields["program"]
        offering_field = self.fields["program_offering"]
        if not isinstance(program_field, forms.ModelChoiceField):
            raise TypeError("program must be a ModelChoiceField")
        if not isinstance(offering_field, forms.ModelChoiceField):
            raise TypeError("program_offering must be a ModelChoiceField")

        program_field.widget.attrs.update(
            {
                "class": "searchable-single",
                "data-placeholder": "Search program or university",
            }
        )
        offering_field.required = False
        offering_field.widget.attrs.update(
            {
                "class": "searchable-single dependent-offering",
                "data-placeholder": "Select program first",
                "disabled": True,
            }
        )

        if self.is_bound:
            program_field.queryset = Program.objects.filter(is_active=True).select_related(
                "university"
            )
            offering_field.queryset = ProgramOffering.objects.filter(is_active=True).select_related(
                "program", "academic_year", "semester"
            )
        else:
            program_field.queryset = Program.objects.none()
            offering_field.queryset = ProgramOffering.objects.none()

    def clean(self):
        cleaned = super().clean() or {}
        program = cleaned.get("program")
        offering = cleaned.get("program_offering")
        if program is not None and offering is not None and offering.program_id != program.pk:
            self.add_error(
                "program_offering",
                _("The selected intake must belong to the selected program."),
            )
        return cleaned
