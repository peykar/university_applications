from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.universities.models import Program

from .forms import (
    ApplyProgramForm,
    LeadDocumentForm,
    LeadForm,
    LeadMessageForm,
    LeadPreferenceForm,
)
from .models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadMessage,
    LeadMessageAttachment,
    LeadMessageRead,
    LeadMessageSenderType,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadProgramInterestStatus,
)
from .services.messaging import ensure_conversation


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
                                "status": LeadProgramInterestStatus.INTERESTED,
                                "created_by": request.user,
                                "updated_by": request.user,
                            },
                        )
            messages.success(request, "Applicant profile created.")
            return redirect("lead-detail", lead_id=lead.pk)
    else:
        form = LeadForm(
            initial={
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

    message_qs = conversation.messages.select_related("sender").prefetch_related(
        "attachments"
    )
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
            "activities": lead.activities.filter(
                is_customer_visible=True
            ).order_by("-created_at")[:20],
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
@require_POST
def lead_interest_response(request, lead_id, interest_id):
    lead = _customer_lead(request.user, lead_id)
    interest = get_object_or_404(
        LeadProgramInterest,
        pk=interest_id,
        lead=lead,
    )

    response = request.POST.get("response")
    if response == "interested":
        interest.status = LeadProgramInterestStatus.INTERESTED
    elif response == "declined":
        interest.status = LeadProgramInterestStatus.DECLINED
    elif response == "shortlisted":
        interest.status = LeadProgramInterestStatus.SHORTLISTED
    else:
        raise Http404

    interest.user_responded_at = timezone.now()
    interest.updated_by = request.user
    interest.save(
        update_fields=(
            "status",
            "user_responded_at",
            "updated_by",
            "updated_at",
        )
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.PROGRAM_RESPONSE,
        description=(
            f"Program response: {interest.program.name_en} → "
            f"{interest.get_status_display()}."
        ),
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    return redirect("lead-detail", lead_id=lead.pk)


@login_required
def apply_program(request, slug):
    program = get_object_or_404(
        Program.objects.select_related("university"),
        slug_en=slug,
        is_active=True,
        university__is_active=True,
    )

    if request.method == "POST":
        form = ApplyProgramForm(
            request.POST,
            user=request.user,
            program=program,
        )
        if form.is_valid():
            lead = form.cleaned_data["lead"]
            offering = form.cleaned_data["offering"]

            interest, created = LeadProgramInterest.objects.get_or_create(
                lead=lead,
                program=program,
                program_offering=offering,
                defaults={
                    "source": LeadProgramInterestSource.USER,
                    "status": LeadProgramInterestStatus.INTERESTED,
                    "created_by": request.user,
                    "updated_by": request.user,
                },
            )

            if not created and interest.status == LeadProgramInterestStatus.DECLINED:
                interest.status = LeadProgramInterestStatus.INTERESTED
                interest.source = LeadProgramInterestSource.USER
                interest.updated_by = request.user
                interest.save(
                    update_fields=(
                        "status",
                        "source",
                        "updated_by",
                        "updated_at",
                    )
                )

            LeadActivity.objects.create(
                lead=lead,
                activity_type=LeadActivityType.PROGRAM_ADDED,
                description=f"Program added: {program.name_en}.",
                is_customer_visible=True,
                created_by=request.user,
                updated_by=request.user,
            )

            messages.success(request, "Program added to the applicant.")
            return redirect("lead-detail", lead_id=lead.pk)
    else:
        form = ApplyProgramForm(user=request.user, program=program)

    return render(
        request,
        "leads/apply_program.html",
        {
            "program": program,
            "form": form,
        },
    )
