from __future__ import annotations

from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.universities.models import Program

from .forms import (
    ApplyProgramForm,
    LeadDocumentForm,
    LeadDocumentReplacementForm,
    LeadForm,
    LeadMessageForm,
    LeadPreferenceForm,
)
from .models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocument,
    LeadDocumentReviewStatus,
    LeadDocumentVersion,
    LeadMessage,
    LeadMessageAttachment,
    LeadMessageRead,
    LeadMessageSenderType,
    LeadProgramInterest,
    LeadProgramInterestSource,
)
from .services.messaging import ensure_conversation, send_system_message


def _customer_lead(user, lead_id):
    return get_object_or_404(
        Lead.objects.select_related(
            "nationality",
            "country_of_residence",
            "assigned_to",
            "converted_student",
        ),
        pk=lead_id,
        user=user,
    )


@login_required
def lead_list(request):
    leads = (
        Lead.objects.filter(user=request.user)
        .select_related("converted_student")
        .prefetch_related("program_interests")
        .order_by("-updated_at")
    )
    return render(request, "leads/lead_list.html", {"leads": leads})


@login_required
def lead_create(request):
    next_program = request.GET.get("next_program") or request.POST.get("next_program")

    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                lead = form.save(commit=False)
                lead.user = request.user
                lead.source = "website"
                lead.created_by = request.user
                lead.updated_by = request.user
                lead.save()

                if next_program:
                    program = Program.objects.filter(
                        slug_en=next_program,
                        is_active=True,
                    ).first()
                    if program:
                        LeadProgramInterest.objects.get_or_create(
                            lead=lead,
                            program=program,
                            program_offering=None,
                            defaults={
                                "source": LeadProgramInterestSource.USER,
                                "created_by": request.user,
                                "updated_by": request.user,
                            },
                        )
            messages.success(request, "Applicant profile created.")
            return redirect("lead-detail", lead_id=lead.pk)
    else:
        form = LeadForm(
            initial={
                "applicant_for": "self",
                "first_name": request.user.first_name or "",
                "last_name": request.user.last_name or "",
                "email": request.user.email or "",
                "cell": request.user.cell or "",
            }
        )

    return render(
        request,
        "leads/lead_form.html",
        {
            "form": form,
            "next_program": next_program,
            "title": "Add applicant",
        },
    )


@login_required
def lead_edit(request, lead_id):
    lead = _customer_lead(request.user, lead_id)

    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.updated_by = request.user
            lead.save()
            messages.success(request, "Applicant profile updated.")
            return redirect("lead-detail", lead_id=lead.pk)
    else:
        form = LeadForm(instance=lead)

    return render(
        request,
        "leads/lead_form.html",
        {"form": form, "lead": lead, "title": "Edit applicant"},
    )


@login_required
def lead_preferences(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    preferences = lead.preferences

    if request.method == "POST":
        form = LeadPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.updated_by = request.user
            if not preferences.created_by_id:
                preferences.created_by = request.user
            preferences.save()
            form.save_m2m()

            lead.needs_program_recommendation = True
            lead.updated_by = request.user
            lead.save(
                update_fields=(
                    "needs_program_recommendation",
                    "updated_by",
                    "updated_at",
                )
            )
            messages.success(request, "Study preferences updated.")
            return redirect("lead-detail", lead_id=lead.pk)
    else:
        form = LeadPreferenceForm(instance=preferences)

    return render(
        request,
        "leads/lead_preferences.html",
        {"lead": lead, "form": form},
    )


@login_required
def lead_detail(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    conversation = ensure_conversation(lead)

    message_qs = conversation.messages.select_related("sender").prefetch_related("attachments")
    for message in message_qs.exclude(sender=request.user):
        LeadMessageRead.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={
                "created_by": request.user,
                "updated_by": request.user,
            },
        )

    interests = lead.program_interests.select_related(
        "program",
        "program__university",
        "program__program_language",
        "program_offering",
        "program_offering__academic_year",
        "program_offering__semester",
    ).order_by("-created_at")

    return render(
        request,
        "leads/lead_detail.html",
        {
            "lead": lead,
            "interests": interests,
            "documents": lead.documents.order_by("-created_at"),
            "conversation": conversation,
            "lead_messages": message_qs,
            "message_form": LeadMessageForm(),
            "document_form": LeadDocumentForm(),
            "replacement_form": LeadDocumentReplacementForm(),
            "activities": lead.activities.filter(is_customer_visible=True).order_by("-created_at")[
                :20
            ],
        },
    )


@login_required
@require_POST
def lead_document_upload(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    form = LeadDocumentForm(request.POST, request.FILES)

    if form.is_valid():
        document = form.save(commit=False)
        document.lead = lead
        document.created_by = request.user
        document.updated_by = request.user
        document.save()

        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivityType.DOCUMENT_UPLOADED,
            description=f"Document uploaded: {document.get_document_type_display()}",
            is_customer_visible=True,
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, "Document uploaded.")
    else:
        messages.error(request, "Could not upload the document.")

    return redirect("lead-detail", lead_id=lead.pk)


@login_required
@require_POST
def lead_document_replace(request, lead_id, document_id):
    lead = _customer_lead(request.user, lead_id)
    document = get_object_or_404(
        LeadDocument.objects.select_related("reviewed_by"),
        pk=document_id,
        lead=lead,
        review_status=LeadDocumentReviewStatus.REPLACEMENT_REQUESTED,
    )
    form = LeadDocumentReplacementForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Choose a replacement file.")
        return redirect("lead-detail", lead_id=lead.pk)

    replacement = form.cleaned_data["file"]

    document.file.open("rb")
    try:
        archived_content = ContentFile(document.file.read())
    finally:
        document.file.close()

    version = LeadDocumentVersion(
        document=document,
        original_name=document.name or Path(document.file.name).name,
        review_status=document.review_status,
        review_note=document.review_note,
        reviewed_by=document.reviewed_by,
        reviewed_at=document.reviewed_at,
        created_by=request.user,
        updated_by=request.user,
    )
    version.file.save(
        Path(document.file.name).name,
        archived_content,
        save=False,
    )
    version.save()

    document.file = replacement
    document.name = replacement.name
    document.review_status = LeadDocumentReviewStatus.PENDING
    document.review_note = ""
    document.reviewed_by = None
    document.reviewed_at = None
    document.is_verified = False
    document.updated_by = request.user
    document.save(
        update_fields=(
            "file",
            "name",
            "review_status",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "is_verified",
            "updated_by",
            "updated_at",
        )
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.DOCUMENT_UPLOADED,
        description=f"Replacement uploaded: {document.get_document_type_display()}",
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    send_system_message(
        lead,
        (
            f"A replacement was uploaded for "
            f"{document.get_document_type_display()}. It is now pending review."
        ),
        performed_by=request.user,
    )
    messages.success(request, "Replacement uploaded and sent for review.")
    return redirect("lead-detail", lead_id=lead.pk)


@login_required
@require_POST
def lead_send_message(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    conversation = ensure_conversation(lead)

    if conversation.is_closed:
        messages.error(request, "This conversation is closed.")
        return redirect("lead-detail", lead_id=lead.pk)

    form = LeadMessageForm(request.POST, request.FILES)
    if form.is_valid():
        message = LeadMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            sender_type=LeadMessageSenderType.CUSTOMER,
            body=form.cleaned_data.get("body", ""),
            created_by=request.user,
            updated_by=request.user,
        )

        attachment = form.cleaned_data.get("attachment")
        if attachment:
            LeadMessageAttachment.objects.create(
                message=message,
                file=attachment,
                original_name=attachment.name,
                content_type=getattr(attachment, "content_type", ""),
                size=getattr(attachment, "size", None),
                created_by=request.user,
                updated_by=request.user,
            )
    else:
        messages.error(request, "Write a message or attach a file.")

    return redirect("lead-detail", lead_id=lead.pk)


@login_required
def apply_program(request, slug):
    program = get_object_or_404(
        Program.objects.select_related(
            "university",
            "program_language",
        ),
        slug_en=slug,
        is_active=True,
        university__is_active=True,
    )

    form = ApplyProgramForm(
        request.POST or None,
        user=request.user,
        program=program,
    )

    if request.method == "POST" and form.is_valid():
        applicant_choice = form.cleaned_data["applicant"]
        offering = form.cleaned_data["offering"]

        with transaction.atomic():
            lead = form.cleaned_data.get("selected_lead")
            if lead is None:
                is_self = applicant_choice == "self_new"
                lead = Lead.objects.create(
                    user=request.user,
                    first_name=(
                        form.cleaned_data.get("new_first_name", "")
                        if applicant_choice in {"self_new", "new"}
                        else ""
                    ),
                    last_name=(
                        form.cleaned_data.get("new_last_name", "")
                        if applicant_choice in {"self_new", "new"}
                        else ""
                    ),
                    email=(
                        form.cleaned_data.get("new_email", "")
                        if applicant_choice in {"self_new", "new"}
                        else ""
                    ),
                    cell=(
                        form.cleaned_data.get("new_cell", "")
                        if applicant_choice in {"self_new", "new"}
                        else ""
                    ),
                    source="website",
                    created_by=request.user,
                    updated_by=request.user,
                )
                if is_self and not lead.email:
                    lead.email = request.user.email or ""
                    lead.save(update_fields=("email", "updated_at"))

            LeadProgramInterest.objects.get_or_create(
                lead=lead,
                program=program,
                program_offering=offering,
                defaults={
                    "source": LeadProgramInterestSource.USER,
                    "created_by": request.user,
                    "updated_by": request.user,
                },
            )

            LeadActivity.objects.create(
                lead=lead,
                activity_type=LeadActivityType.PROGRAM_ADDED,
                description=f"Program added: {program.name_en}.",
                is_customer_visible=True,
                created_by=request.user,
                updated_by=request.user,
            )

        messages.success(request, f"{program.name_en} added to the applicant programs.")
        return redirect("lead-detail", lead_id=lead.pk)

    return render(
        request,
        "leads/apply_program.html",
        {
            "program": program,
            "form": form,
            "applicant_options": form.applicant_options,
        },
    )
