from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.applications.models import Application, ApplicationStatus
from apps.leads.forms import LeadMessageForm
from apps.leads.models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocument,
    LeadMessage,
    LeadMessageAttachment,
    LeadMessageRead,
    LeadMessageSenderType,
    LeadProgramInterest,
    LeadProgramInterestStatus,
    LeadStatus,
)
from apps.leads.services.messaging import ensure_conversation

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
    ).exclude(
        status__in=(
            LeadProgramInterestStatus.DECLINED,
            LeadProgramInterestStatus.CONVERTED,
        )
    )

    context = {
        "lead_count": leads.count(),
        "new_lead_count": leads.filter(status=LeadStatus.NEW).count(),
        "needs_info_count": leads.filter(status=LeadStatus.NEEDS_INFO).count(),
        "recommendation_count": leads.filter(needs_program_recommendation=True)
        .exclude(status__in=(LeadStatus.CONVERTED, LeadStatus.REJECTED))
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
    leads = _agent_leads(request.user).select_related("agent", "user")
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
    lead_messages = conversation.messages.select_related("sender").prefetch_related("attachments")

    unread = lead_messages.filter(sender_type=LeadMessageSenderType.CUSTOMER).exclude(
        read_receipts__user=request.user
    )
    for message in unread:
        LeadMessageRead.objects.get_or_create(
            message=message,
            user=request.user,
            defaults={"created_by": request.user, "updated_by": request.user},
        )

    return render(
        request,
        "agents/applicant_detail.html",
        {
            "lead": lead,
            "lead_messages": lead_messages,
            "conversation": conversation,
            "message_form": LeadMessageForm(),
            "documents": lead.documents.order_by("-created_at"),
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
    lead = get_object_or_404(_agent_leads(request.user), pk=lead_id)
    status = request.POST.get("status")
    if status not in LeadStatus.values:
        messages.error(request, "Invalid applicant status.")
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    old_status = lead.status
    lead.status = status
    lead.updated_by = request.user
    lead.save(update_fields=("status", "updated_by", "updated_at"))

    if old_status != status:
        LeadActivity.objects.create(
            lead=lead,
            activity_type=LeadActivityType.STATUS_CHANGED,
            description=(
                f"Agent changed status from {LeadStatus(old_status).label} "
                f"to {LeadStatus(status).label}."
            ),
            is_customer_visible=True,
            created_by=request.user,
            updated_by=request.user,
        )
    messages.success(request, "Applicant status updated.")
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
@require_POST
def program_request_status(request, interest_id):
    interest = get_object_or_404(
        LeadProgramInterest.objects.filter(lead__in=_agent_leads(request.user)),
        pk=interest_id,
        source="user",
    )
    status = request.POST.get("status")
    allowed = {
        LeadProgramInterestStatus.INTERESTED,
        LeadProgramInterestStatus.SHORTLISTED,
        LeadProgramInterestStatus.QUALIFIED,
        LeadProgramInterestStatus.DECLINED,
    }
    if status not in allowed:
        messages.error(request, "Invalid program request status.")
        return redirect("agent-application-list")

    interest.status = status
    interest.updated_by = request.user
    interest.save(update_fields=("status", "updated_by", "updated_at"))
    messages.success(request, "Program request status updated.")
    return redirect("agent-application-list")


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
