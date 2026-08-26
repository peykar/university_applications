from django import forms
from django.utils.translation import gettext_lazy as _

from apps.leads.models import DocumentType, LeadDocumentReviewStatus


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
