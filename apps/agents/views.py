from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.applications.models import Application, ApplicationStatus
from apps.leads.forms import LeadMessageForm
from apps.leads.models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocument,
    LeadDocumentReviewHistory,
    LeadDocumentReviewStatus,
    LeadMessage,
    LeadMessageAttachment,
    LeadMessageRead,
    LeadMessageSenderType,
    LeadProgramInterest,
    LeadStatus,
)
from apps.leads.services.conversion import convert_lead_to_student, finalize_lead
from apps.leads.services.messaging import ensure_conversation, send_system_message

from .forms import DocumentReviewForm, PromoteChatAttachmentForm
from .models import Agent


def _agent_ids(user) -> list:
    if user.is_superuser:
        return list(Agent.objects.filter(is_active=True).values_list("pk", flat=True))
    return list(user.agents.filter(is_active=True).values_list("pk", flat=True))


def _require_agent(user) -> list:
    agent_ids = _agent_ids(user)
    if not agent_ids:
        raise PermissionDenied("An active agent membership is required.")
    return agent_ids


def _agent_leads(user):
    agent_ids = _require_agent(user)
    return Lead.objects.filter(agent_id__in=agent_ids)


def _agent_applications(user):
    agent_ids = _require_agent(user)
    return Application.objects.filter(
        Q(agent_id__in=agent_ids) | Q(agent__isnull=True, student__agent_id__in=agent_ids)
    ).distinct()


def _render_agent_not_found(
    request,
    *,
    resource_name: str,
    list_url_name: str,
):
    """Render a privacy-safe 404 without revealing cross-agent resource existence."""
    response = render(
        request,
        "errors/404.html",
        {
            "error_message": (
                f"We couldn't find this {resource_name}, or it isn't available "
                "in your agent workspace."
            ),
            "primary_url": reverse(list_url_name),
            "primary_label": f"Back to {resource_name}s",
            "secondary_url": reverse("agent-dashboard"),
            "secondary_label": "Agent workspace",
        },
        status=404,
    )
    response["X-TurkDemy-Error-Page"] = "1"
    return response


@login_required
def dashboard(request):
    leads = _agent_leads(request.user)
    applications = _agent_applications(request.user)

    unread_messages = LeadMessage.objects.filter(
        conversation__lead__in=leads,
        sender_type=LeadMessageSenderType.CUSTOMER,
    ).exclude(read_receipts__user=request.user)
    program_requests = LeadProgramInterest.objects.filter(
        lead__in=leads,
        source="user",
    )

    context = {
        "lead_count": leads.count(),
        "new_lead_count": leads.filter(status=LeadStatus.NEW).count(),
        "assigned_lead_count": leads.filter(status=LeadStatus.ASSIGNED).count(),
        "recommendation_count": leads.filter(needs_program_recommendation=True)
        .exclude(status__in=(LeadStatus.FINALIZED, LeadStatus.CLOSED))
        .count(),
        "unread_message_count": unread_messages.count(),
        "application_count": applications.count(),
        "application_action_count": (
            applications.filter(
                status__in=(
                    ApplicationStatus.SUBMITTED,
                    ApplicationStatus.UNDER_REVIEW,
                    ApplicationStatus.ADDITIONAL_DOCUMENTS,
                )
            ).count()
            + program_requests.count()
        ),
        "unverified_document_count": LeadDocument.objects.filter(
            lead__in=leads,
            is_verified=False,
        ).count(),
        "recent_leads": leads.select_related("agent", "user").order_by("-updated_at")[:8],
        "recent_messages": unread_messages.select_related("conversation__lead", "sender").order_by(
            "-created_at"
        )[:8],
        "recent_program_requests": program_requests.select_related(
            "lead", "program", "program__university", "program_offering"
        ).order_by("-updated_at")[:8],
        "recent_applications": applications.select_related(
            "student",
            "program_offering__program",
            "program_offering__program__university",
        ).order_by("-updated_at")[:8],
    }
    return render(request, "agents/workspace_dashboard.html", context)


@login_required
def applicant_list(request):
    leads = _agent_leads(request.user).select_related("agent", "user", "assigned_to")
    status = (request.GET.get("status") or "").strip()
    query = (request.GET.get("q") or "").strip()

    if status in LeadStatus.values:
        leads = leads.filter(status=status)
    if query:
        leads = leads.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(user__email__icontains=query)
        )

    return render(
        request,
        "agents/applicant_list.html",
        {
            "leads": leads.order_by("-updated_at"),
            "status_choices": LeadStatus.choices,
            "selected_status": status,
            "query": query,
        },
    )


@login_required
def applicant_detail(request, lead_id):
    lead = (
        _agent_leads(request.user)
        .select_related("agent", "user", "converted_student", "assigned_to")
        .filter(pk=lead_id)
        .first()
    )
    if lead is None:
        return _render_agent_not_found(
            request,
            resource_name="applicant",
            list_url_name="agent-applicant-list",
        )
    conversation = ensure_conversation(lead)
    lead_messages = conversation.messages.select_related("sender").prefetch_related(
        "attachments__promoted_document"
    )

    unread = lead_messages.filter(sender_type=LeadMessageSenderType.CUSTOMER).exclude(
        read_receipts__user=request.user
    )
    for message in unread:
        LeadMessageRead.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={"created_by": request.user, "updated_by": request.user},
        )

    agent_users = (
        lead.agent.users.filter(is_active=True).order_by(
            "first_name", "last_name", "email", "username"
        )
        if lead.agent_id
        else []
    )

    return render(
        request,
        "agents/applicant_detail.html",
        {
            "lead": lead,
            "agent_users": agent_users,
            "lead_messages": lead_messages,
            "conversation": conversation,
            "message_form": LeadMessageForm(),
            "document_review_form": DocumentReviewForm(),
            "promote_attachment_form": PromoteChatAttachmentForm(),
            "documents": lead.documents.select_related(
                "reviewed_by",
                "source_message_attachment",
            ).order_by("-created_at"),
            "interests": lead.program_interests.select_related(
                "program", "program__university", "program_offering"
            ).order_by("-created_at"),
            "activities": lead.activities.order_by("-created_at")[:30],
            "status_choices": LeadStatus.choices,
        },
    )


@login_required
@require_POST
def applicant_status(request, lead_id):
    """Only closing/reopening is manually controlled; other statuses are derived."""
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    action = (request.POST.get("action") or "").strip()

    if action == "close":
        if lead.status == LeadStatus.FINALIZED:
            messages.error(request, "A finalized applicant cannot be closed.")
            return redirect("agent-applicant-detail", lead_id=lead.pk)
        reason = (request.POST.get("close_reason") or "").strip()
        lead.status = LeadStatus.CLOSED
        lead.closed_at = timezone.now()
        lead.closed_by = request.user
        lead.close_reason = reason
        lead.updated_by = request.user
        lead.save(
            update_fields=(
                "status",
                "closed_at",
                "closed_by",
                "close_reason",
                "updated_by",
                "updated_at",
            )
        )
        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivityType.CLOSED,
            description=f"Lead closed.{f' Reason: {reason}' if reason else ''}",
            is_customer_visible=False,
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, "Applicant closed.")
    elif action == "reopen" and lead.status == LeadStatus.CLOSED:
        lead.status = LeadStatus.ASSIGNED if lead.assigned_to_id else LeadStatus.NEW
        lead.closed_at = None
        lead.closed_by = None
        lead.close_reason = ""
        lead.updated_by = request.user
        # Lead.save derives NEW/ASSIGNED from assigned_to.
        lead.save(
            update_fields=(
                "status",
                "closed_at",
                "closed_by",
                "close_reason",
                "updated_by",
                "updated_at",
            )
        )
        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivityType.REOPENED,
            description="Lead reopened.",
            is_customer_visible=False,
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, "Applicant reopened.")
    else:
        messages.error(request, "Invalid applicant status action.")

    return redirect("agent-applicant-detail", lead_id=lead.pk)


def _user_display_name(user) -> str:
    return user.get_full_name() or user.get_username() or user.email


def _assign_lead(lead, *, target_user, performed_by) -> None:
    previous = lead.assigned_to
    lead.assigned_to = target_user
    lead.updated_by = performed_by
    lead.save(update_fields=("assigned_to", "updated_by", "updated_at"))

    if previous == target_user:
        return

    if previous:
        activity_type = LeadActivityType.REASSIGNED
        description = (
            f"Reassigned from {_user_display_name(previous)} to {_user_display_name(target_user)}."
        )
    else:
        activity_type = LeadActivityType.ASSIGNED
        description = f"Assigned to {_user_display_name(target_user)}."

    LeadActivity.objects.create(
        lead=lead,
        activity_type=activity_type,
        description=description,
        is_customer_visible=False,
        created_by=performed_by,
        updated_by=performed_by,
    )


@login_required
@require_POST
def applicant_assign_to_me(request, lead_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(request, "This applicant can no longer be assigned.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if lead.assigned_to_id == request.user.pk:
        messages.info(request, "You are already responsible for this applicant.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if not lead.agent_id or not lead.agent.users.filter(pk=request.user.pk).exists():
        messages.error(request, "You are not an active user of this applicant's agent.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    _assign_lead(
        lead,
        target_user=request.user,
        performed_by=request.user,
    )
    messages.success(request, "You are now responsible for this applicant.")
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_assign(request, lead_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(request, "This applicant can no longer be assigned.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    user_id = (request.POST.get("user_id") or "").strip()
    if not user_id or not lead.agent_id:
        messages.error(request, "Choose a responsible agent user.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    target_user = lead.agent.users.filter(
        pk=user_id,
        is_active=True,
    ).first()
    if target_user is None:
        messages.error(
            request,
            "The selected user does not belong to this applicant's agent.",
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if lead.assigned_to_id == target_user.pk:
        messages.info(request, "This user is already responsible for the applicant.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    _assign_lead(
        lead,
        target_user=target_user,
        performed_by=request.user,
    )
    messages.success(
        request,
        f"{_user_display_name(target_user)} is now responsible for this applicant.",
    )
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_finalize(request, lead_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)

    if lead.status == LeadStatus.CLOSED:
        messages.error(request, "Reopen this applicant before finalizing it.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)
    if lead.status == LeadStatus.FINALIZED:
        messages.info(request, "This applicant is already finalized.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)
    if lead.assigned_to_id != request.user.pk:
        messages.error(
            request,
            "Assign this applicant to yourself before finalizing it.",
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    try:
        finalize_lead(lead, performed_by=request.user)
        student = convert_lead_to_student(lead, performed_by=request.user)
    except ValidationError as exc:
        if hasattr(exc, "message_dict"):
            detail = " ".join(
                message
                for field_messages in exc.message_dict.values()
                for message in field_messages
            )
        else:
            detail = " ".join(exc.messages)
        messages.error(
            request,
            f"Applicant cannot be finalized yet. {detail}",
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    messages.success(
        request,
        f"Applicant finalized and converted to student {student}.",
    )
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_message(request, lead_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    conversation = ensure_conversation(lead)
    if conversation.is_closed:
        messages.error(request, "This conversation is closed.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    form = LeadMessageForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Write a message or attach a file.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    message = LeadMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        sender_type=LeadMessageSenderType.STAFF,
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
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_document_review(request, lead_id, document_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    document = get_object_or_404(LeadDocument, pk=document_id, lead=lead)
    form = DocumentReviewForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Choose a valid document review decision.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    review_status = form.cleaned_data["review_status"]
    document.review_status = review_status
    document.review_note = form.cleaned_data["review_note"]
    document.reviewed_by = request.user
    document.reviewed_at = timezone.now()
    document.is_verified = review_status == LeadDocumentReviewStatus.APPROVED
    document.updated_by = request.user
    document.save(
        update_fields=(
            "review_status",
            "review_note",
            "reviewed_by",
            "reviewed_at",
            "is_verified",
            "updated_by",
            "updated_at",
        )
    )

    LeadDocumentReviewHistory.objects.create(
        document=document,
        review_status=review_status,
        review_note=document.review_note,
        reviewed_by=request.user,
        reviewed_at=document.reviewed_at,
        created_by=request.user,
        updated_by=request.user,
    )

    if review_status == LeadDocumentReviewStatus.REPLACEMENT_REQUESTED:
        reason = document.review_note.strip()
        body = f"A replacement has been requested for {document.get_document_type_display()}."
        if reason:
            body += f" Reason: {reason}"
        send_system_message(lead, body, performed_by=request.user)

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.DOCUMENT_REVIEWED,
        description=(
            f"Document reviewed: {document.name or document.get_document_type_display()} "
            f"→ {document.get_review_status_display()}."
        ),
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, "Document review updated.")
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_attachment_to_document(request, lead_id, attachment_id):
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    attachment = get_object_or_404(
        LeadMessageAttachment.objects.select_related(
            "message",
            "message__conversation",
        ),
        pk=attachment_id,
        message__conversation__lead=lead,
        message__sender_type=LeadMessageSenderType.CUSTOMER,
    )

    if hasattr(attachment, "promoted_document"):
        messages.info(request, "This attachment is already in Documents.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    form = PromoteChatAttachmentForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Choose a document type before adding the attachment.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    attachment.file.open("rb")
    try:
        content = ContentFile(attachment.file.read())
    finally:
        attachment.file.close()

    document = LeadDocument(
        lead=lead,
        document_type=form.cleaned_data["document_type"],
        name=form.cleaned_data["name"] or attachment.original_name,
        description=form.cleaned_data["description"],
        review_status=LeadDocumentReviewStatus.PENDING,
        source_message_attachment=attachment,
        created_by=request.user,
        updated_by=request.user,
    )
    document.file.save(
        attachment.original_name or "attachment",
        content,
        save=False,
    )
    document.save()

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.DOCUMENT_UPLOADED,
        description=(
            f"Chat attachment added to Documents: "
            f"{document.name or document.get_document_type_display()}."
        ),
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, "Attachment added to Documents and marked for review.")
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
def message_inbox(request):
    leads = _agent_leads(request.user)
    conversations = (
        leads.filter(conversation__isnull=False)
        .select_related("conversation", "user")
        .annotate(
            unread_count=Count(
                "conversation__messages",
                filter=Q(conversation__messages__sender_type=LeadMessageSenderType.CUSTOMER)
                & ~Q(conversation__messages__read_receipts__user=request.user),
                distinct=True,
            )
        )
        .filter(conversation__messages__isnull=False)
        .annotate(last_message_at=Max("conversation__messages__created_at"))
        .distinct()
        .order_by("-last_message_at")
    )
    return render(request, "agents/message_inbox.html", {"leads": conversations})


@login_required
def application_list(request):
    leads = _agent_leads(request.user)
    program_requests = LeadProgramInterest.objects.filter(
        lead__in=leads,
        source="user",
    ).select_related(
        "lead",
        "program",
        "program__university",
        "program_offering",
    )
    applications = _agent_applications(request.user).select_related(
        "student",
        "agent",
        "program_offering__program",
        "program_offering__program__university",
    )
    status = (request.GET.get("status") or "").strip()
    if status in ApplicationStatus.values:
        applications = applications.filter(status=status)

    return render(
        request,
        "agents/application_list.html",
        {
            "program_requests": program_requests.order_by("-updated_at"),
            "applications": applications.order_by("-updated_at"),
            "status_choices": ApplicationStatus.choices,
            "selected_status": status,
        },
    )


@login_required
def application_detail(request, application_id):
    application = (
        _agent_applications(request.user)
        .select_related(
            "student",
            "agent",
            "program_offering__program",
            "program_offering__program__university",
        )
        .prefetch_related("documents__student_document")
        .filter(pk=application_id)
        .first()
    )
    if application is None:
        return _render_agent_not_found(
            request,
            resource_name="application",
            list_url_name="agent-application-list",
        )
    return render(
        request,
        "agents/application_detail.html",
        {
            "application": application,
            "status_choices": ApplicationStatus.choices,
        },
    )


@login_required
@require_POST
def application_status(request, application_id):
    application = get_object_or_404(
        _agent_applications(request.user),
        pk=application_id,
    )
    status = request.POST.get("status")
    if status not in ApplicationStatus.values:
        messages.error(request, "Invalid application status.")
        return redirect("agent-application-detail", application_id=application.pk)

    application.status = status
    application.updated_by = request.user
    application.save(update_fields=("status", "updated_by", "updated_at"))
    messages.success(request, "Application status updated.")
    return redirect("agent-application-detail", application_id=application.pk)
