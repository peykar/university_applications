from __future__ import annotations

from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.messaging.forms import MessageForm
from apps.messaging.models import (
    Conversation,
    ConversationParticipantRole,
    Message,
    MessageSenderRole,
)
from apps.messaging.services import (
    mark_conversation_read,
    send_message,
    unread_count_for_conversation,
)
from apps.universities.models import DegreeType, Program, ProgramOffering, UniversityType

from .forms import (
    ApplyProgramForm,
    CustomerLeadEditForm,
    LeadDocumentForm,
    LeadDocumentReplacementForm,
    LeadForm,
    LeadPreferenceForm,
)
from .models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocument,
    LeadDocumentReviewStatus,
    LeadDocumentVersion,
    LeadProgramInterest,
    LeadProgramInterestSource,
    LeadStatus,
)
from .services.activity import record_applicant_profile_update
from .services.messaging import ensure_conversation, send_system_message


def _customer_lead(user, lead_id):
    return get_object_or_404(
        Lead.objects.select_related(
            "nationality",
            "country_of_birth",
            "country_of_residence",
            "assigned_to",
            "converted_student",
        ),
        pk=lead_id,
        user=user,
    )


def _customer_activity_label(activity: LeadActivity) -> str:
    activity_type = activity.activity_type
    detail = activity.description.partition(":")[2].strip().rstrip(".")
    labels: dict[str, str] = {
        LeadActivityType.CREATED: _("Request created"),
        LeadActivityType.APPLICANT_UPDATED: _("Profile updated"),
        LeadActivityType.STATUS_CHANGED: _("Request status updated"),
        LeadActivityType.ASSIGNED: _("Advisor assigned"),
        LeadActivityType.REASSIGNED: _("Advisor changed"),
        LeadActivityType.CLOSED: _("Request closed"),
        LeadActivityType.REOPENED: _("Request reopened"),
        LeadActivityType.VALIDATED: _("Request reviewed"),
        LeadActivityType.DOCUMENT_UPLOADED: (
            _("%(document)s uploaded") % {"document": detail} if detail else _("Document uploaded")
        ),
        LeadActivityType.DOCUMENT_REVIEWED: (
            _("%(document)s reviewed") % {"document": detail} if detail else _("Document reviewed")
        ),
        LeadActivityType.PROGRAM_ADDED: (
            _("%(program)s added to your request") % {"program": detail}
            if detail
            else _("Program added to your request")
        ),
        LeadActivityType.PROGRAM_SUGGESTED: (
            _("Your advisor suggested %(program)s") % {"program": detail}
            if detail
            else _("Your advisor suggested a program")
        ),
        LeadActivityType.PROGRAM_RESPONSE: _("Program response updated"),
        LeadActivityType.RECOMMENDATIONS_GENERATED: _("Program recommendations updated"),
        LeadActivityType.FINALIZED: _("Request completed"),
    }
    return labels.get(activity_type, _("Request updated"))


def _lead_entity_context(*, request, lead, mark_read=False):
    conversation = ensure_conversation(lead) if lead.agent_id else None
    unread_message_count = 0
    message_qs = Message.objects.none()
    if conversation is not None:
        unread_message_count = unread_count_for_conversation(
            conversation=conversation,
            user=request.user,
            participant_role=ConversationParticipantRole.CUSTOMER,
        )
        message_qs = conversation.messages.select_related("sender").prefetch_related("attachments")
        if mark_read:
            mark_conversation_read(
                conversation=conversation,
                user=request.user,
                participant_role=ConversationParticipantRole.CUSTOMER,
            )

    active_offerings = (
        ProgramOffering.objects.filter(is_active=True)
        .select_related("academic_year", "semester")
        .order_by("academic_year__name_en", "semester__name_en")
    )
    interests = (
        lead.program_interests.select_related(
            "program",
            "program__university",
            "program__academic_unit",
            "program_offering",
            "program_offering__academic_year",
            "program_offering__semester",
        )
        .prefetch_related(
            "program__instruction_language_rows__language",
            Prefetch("program__offerings", queryset=active_offerings, to_attr="customer_offerings"),
        )
        .order_by("-created_at")
    )
    documents = list(lead.documents.order_by("-created_at"))
    attention_documents = [
        document
        for document in documents
        if document.review_status == LeadDocumentReviewStatus.REPLACEMENT_REQUESTED
    ]

    preferences = lead.preferences
    degree_labels = dict(DegreeType.choices)
    university_type_labels = dict(UniversityType.choices)
    preferred_degrees = [
        degree_labels.get(code, code) for code in preferences.preferred_degrees or []
    ]
    preferred_university_types = [
        university_type_labels.get(code, code)
        for code in preferences.preferred_university_types or []
    ]

    activity_qs = lead.activities.filter(is_customer_visible=True).order_by("-created_at")[:20]
    customer_activities = [
        {
            "label": _customer_activity_label(activity),
            "created_at": activity.created_at,
        }
        for activity in activity_qs
    ]

    student = lead.converted_student
    applications = (
        student.applications.select_related(
            "program_offering__program",
            "program_offering__program__university",
        ).order_by("-updated_at")
        if student is not None
        else []
    )

    return {
        "lead": lead,
        "interests": interests,
        "documents": documents,
        "attention_documents": attention_documents,
        "needs_attention": bool(unread_message_count or attention_documents),
        "has_required_action": bool(attention_documents),
        "unread_message_count": unread_message_count,
        "conversation": conversation,
        "lead_messages": message_qs,
        "recent_messages": message_qs.order_by("-created_at")[:3],
        "message_form": MessageForm(),
        "document_form": LeadDocumentForm(),
        "replacement_form": LeadDocumentReplacementForm(),
        "activities": customer_activities,
        "applications": applications,
        "preferences": preferences,
        "preferred_degrees": preferred_degrees,
        "preferred_university_types": preferred_university_types,
        "preferred_languages": preferences.preferred_languages.all(),
        "preferred_cities": preferences.preferred_cities.all(),
        "preferred_universities": preferences.preferred_universities.all(),
        "preferred_departments": preferences.preferred_departments.all(),
        "agent_context": False,
    }


@login_required
def lead_list(request):
    leads = list(
        Lead.objects.filter(user=request.user)
        .select_related("converted_student")
        .prefetch_related(
            "program_interests__program__university",
            "documents",
        )
        .order_by("-updated_at")
    )

    lead_content_type = ContentType.objects.get_for_model(Lead)
    conversations = {
        conversation.subject_object_id: conversation
        for conversation in Conversation.objects.filter(
            customer=request.user,
            subject_content_type=lead_content_type,
            subject_object_id__in=[lead.pk for lead in leads],
        )
    }
    request_cards = []
    for lead in leads:
        programs = list(lead.program_interests.all())
        needs_document_action = any(
            document.review_status == LeadDocumentReviewStatus.REPLACEMENT_REQUESTED
            for document in lead.documents.all()
        )
        conversation = conversations.get(lead.pk)
        unread_message_count = (
            unread_count_for_conversation(
                conversation=conversation,
                user=request.user,
                participant_role=ConversationParticipantRole.CUSTOMER,
            )
            if conversation is not None
            else 0
        )
        request_cards.append(
            {
                "lead": lead,
                "programs": programs,
                "needs_document_action": needs_document_action,
                "unread_message_count": unread_message_count,
                "needs_attention": bool(unread_message_count or needs_document_action),
            }
        )

    return render(request, "leads/lead_list.html", {"request_cards": request_cards})


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
    if lead.status == LeadStatus.FINALIZED:
        messages.error(
            request,
            "This Request profile can no longer be edited.",
        )
        return redirect("lead-profile", lead_id=lead.pk)

    if request.method == "POST":
        form = CustomerLeadEditForm(request.POST, instance=lead)
        if form.is_valid():
            updated_lead = form.save(commit=False)
            updated_lead.updated_by = request.user
            updated_lead.save()

            if record_applicant_profile_update(
                lead=updated_lead,
                form=form,
                actor=request.user,
            ):
                messages.success(request, "Profile updated.")
            else:
                messages.info(request, "No profile data changed.")
            return redirect("lead-profile", lead_id=updated_lead.pk)
    else:
        form = CustomerLeadEditForm(instance=lead)

    return render(
        request,
        "leads/lead_form.html",
        {
            "form": form,
            "lead": lead,
            "title": "Edit profile",
            "entity_tab": "profile",
            "agent_context": False,
        },
    )


@login_required
def lead_preferences(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "preferences"
    return render(request, "leads/lead_section.html", context)


@login_required
def lead_preferences_edit(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    if lead.status == LeadStatus.FINALIZED:
        messages.error(
            request,
            "This Request's preferences can no longer be edited.",
        )
        return redirect("lead-preferences", lead_id=lead.pk)

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
            return redirect("lead-preferences", lead_id=lead.pk)
    else:
        form = LeadPreferenceForm(instance=preferences)

    return render(
        request,
        "leads/lead_preferences.html",
        {
            "lead": lead,
            "form": form,
            "entity_tab": "preferences",
            "agent_context": False,
        },
    )


@login_required
def lead_detail(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "overview"
    return render(request, "leads/lead_detail.html", context)


@login_required
def lead_profile(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "profile"
    return render(request, "leads/lead_section.html", context)


@login_required
def lead_programs(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "programs"
    return render(request, "leads/lead_section.html", context)


@login_required
@require_POST
def lead_program_intake_update(request, lead_id, interest_id):
    lead = _customer_lead(request.user, lead_id)
    if lead.status == LeadStatus.FINALIZED:
        messages.error(request, _("This Request can no longer be changed."))
        return redirect("lead-programs", lead_id=lead.pk)

    interest = get_object_or_404(
        LeadProgramInterest.objects.select_related("program"),
        pk=interest_id,
        lead=lead,
    )
    offering_id = request.POST.get("program_offering", "").strip()
    if not offering_id:
        interest.program_offering = None
    else:
        offering = get_object_or_404(
            ProgramOffering,
            pk=offering_id,
            program=interest.program,
            is_active=True,
        )
        interest.program_offering = offering
    interest.updated_by = request.user
    interest.save(update_fields=("program_offering", "updated_by", "updated_at"))
    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.PROGRAM_RESPONSE,
        description=f"Program intake updated: {interest.program.name_en}.",
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Program intake updated."))
    return redirect("lead-programs", lead_id=lead.pk)


@login_required
@require_POST
def lead_program_remove(request, lead_id, interest_id):
    lead = _customer_lead(request.user, lead_id)
    if lead.status == LeadStatus.FINALIZED:
        messages.error(request, _("This Request can no longer be changed."))
        return redirect("lead-programs", lead_id=lead.pk)

    interest = get_object_or_404(LeadProgramInterest, pk=interest_id, lead=lead)
    program_name = interest.program.name_en
    interest.delete()
    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.PROGRAM_RESPONSE,
        description=f"Program removed: {program_name}.",
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Program removed from this Request."))
    return redirect("lead-programs", lead_id=lead.pk)


@login_required
def lead_documents(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "documents"
    return render(request, "leads/lead_section.html", context)


@login_required
def lead_applications(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead)
    context["entity_tab"] = "applications"
    return render(request, "leads/lead_section.html", context)


@login_required
def lead_messages(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    context = _lead_entity_context(request=request, lead=lead, mark_read=True)
    context["entity_tab"] = "messages"
    return render(request, "leads/lead_section.html", context)


@login_required
@require_POST
def lead_document_upload(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    if lead.status == LeadStatus.FINALIZED:
        messages.error(
            request,
            "Upload documents to the student record after finalization.",
        )
        return redirect("lead-documents", lead_id=lead.pk)

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

    return redirect("lead-documents", lead_id=lead.pk)


@login_required
@require_POST
def lead_document_replace(request, lead_id, document_id):
    lead = _customer_lead(request.user, lead_id)
    if lead.status == LeadStatus.FINALIZED:
        messages.error(
            request,
            "Replace documents on the student record after finalization.",
        )
        return redirect("lead-documents", lead_id=lead.pk)

    document = get_object_or_404(
        LeadDocument.objects.select_related("reviewed_by"),
        pk=document_id,
        lead=lead,
        review_status=LeadDocumentReviewStatus.REPLACEMENT_REQUESTED,
    )
    form = LeadDocumentReplacementForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Choose a replacement file.")
        return redirect("lead-documents", lead_id=lead.pk)

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
    if lead.agent_id:
        send_system_message(
            lead,
            (
                f"A replacement was uploaded for "
                f"{document.get_document_type_display()}. It is now pending review."
            ),
            performed_by=request.user,
        )
    messages.success(request, "Replacement uploaded and sent for review.")
    return redirect("lead-documents", lead_id=lead.pk)


@login_required
@require_POST
def lead_send_message(request, lead_id):
    lead = _customer_lead(request.user, lead_id)
    if not lead.agent_id:
        messages.info(
            request,
            _("Messaging will be available once an advisor is assigned."),
        )
        return redirect("lead-messages", lead_id=lead.pk)

    conversation = ensure_conversation(lead)

    if conversation.is_closed:
        messages.error(request, "This conversation is closed.")
        return redirect("lead-messages", lead_id=lead.pk)

    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        send_message(
            conversation=conversation,
            sender=request.user,
            sender_role=MessageSenderRole.CUSTOMER,
            body=form.cleaned_data.get("body", ""),
            attachment=form.cleaned_data.get("attachment"),
        )
    else:
        messages.error(request, "Write a message or attach a file.")

    return redirect("lead-messages", lead_id=lead.pk)


@login_required
def apply_program(request, slug):
    program = get_object_or_404(
        Program.objects.select_related(
            "university",
            "academic_unit",
        ).prefetch_related("instruction_language_rows__language"),
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
