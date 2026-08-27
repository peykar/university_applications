from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.leads.models import (
    DocumentType,
    Lead,
    LeadDocument,
    LeadDocumentReviewStatus,
)
from apps.students.models import StudentDocument
from apps.universities.models import ProgramOffering


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


class StudentApplicationOfferingForm(forms.Form):
    offering = forms.ModelChoiceField(
        queryset=ProgramOffering.objects.none(),
        label=_("Program / intake"),
    )

    def __init__(self, *args, program=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = ProgramOffering.objects.filter(is_active=True).select_related(
            "program",
            "program__university",
            "academic_year",
            "semester",
        )
        if program is not None:
            queryset = queryset.filter(program=program)
        offering_field = self.fields["offering"]
        if isinstance(offering_field, forms.ModelChoiceField):
            offering_field.queryset = queryset.order_by(
                "program__university__name_en",
                "program__name_en",
                "academic_year__name_en",
                "semester__name_en",
            )


class StudentDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ("document_type", "file", "short_description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["short_description"].widget = forms.Textarea(
            attrs={"rows": 2},
        )


class ApplicationExistingDocumentForm(forms.Form):
    student_document = forms.ModelChoiceField(
        queryset=StudentDocument.objects.none(),
        label=_("Student document"),
    )

    def __init__(self, *args, student=None, application=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = StudentDocument.objects.none()
        if student is not None:
            queryset = student.documents.all()
            if application is not None:
                queryset = queryset.exclude(applications__application=application)
        field = self.fields["student_document"]
        if isinstance(field, forms.ModelChoiceField):
            field.queryset = queryset.order_by("document_type", "-created_at")


class ApplicationDocumentUploadForm(StudentDocumentUploadForm):
    pass
