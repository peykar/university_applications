from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.applications.models import Application, ApplicationDocument, ApplicationStatus
from apps.applications.services import create_student_application
from apps.leads.models import (
    Lead,
    LeadActivity,
    LeadActivityType,
    LeadDocument,
    LeadDocumentReviewHistory,
    LeadDocumentReviewStatus,
    LeadProgramInterest,
    LeadStatus,
)
from apps.leads.services.activity import record_applicant_profile_update
from apps.leads.services.conversion import finalize_lead
from apps.leads.services.messaging import ensure_conversation, send_system_message
from apps.leads.services.recommendations import (
    RecommendationOutcome,
    recommend_program,
)
from apps.messaging.forms import MessageForm
from apps.messaging.models import (
    Conversation,
    ConversationParticipantRole,
    Message,
    MessageAttachment,
    MessageSenderRole,
    SystemMessageEventType,
)
from apps.messaging.services import (
    agent_unread_count,
    get_or_create_conversation,
    mark_conversation_read,
    send_message,
    unread_count_for_conversation,
)
from apps.operations.forms import CommunicationLogForm, TodoForm
from apps.operations.models import CommunicationLog, Todo, TodoStatus
from apps.operations.services import (
    add_todo_comment,
    communications_for_subject_tree,
    create_communication,
    create_todo,
    edit_communication,
    todos_for_subject_tree,
    update_todo,
)
from apps.students.models import Student
from apps.universities.models import Program, ProgramOffering

from .forms import (
    AgentLeadDocumentUploadForm,
    AgentLeadEditForm,
    ApplicationDocumentUploadForm,
    ApplicationExistingDocumentForm,
    DocumentReviewForm,
    PromoteChatAttachmentForm,
    StudentApplicationOfferingForm,
    StudentDocumentUploadForm,
    StudentRecordConversionForm,
)
from .services.context import available_agents, resolve_active_agent, switch_active_agent


def _active_agent(request):
    return resolve_active_agent(request)


def _agent_leads(request):
    return Lead.objects.filter(agent=_active_agent(request))


def _agent_students(request):
    return Student.objects.filter(agent=_active_agent(request))


def _agent_applications(request):
    agent = _active_agent(request)
    return Application.objects.filter(
        Q(agent=agent) | Q(agent__isnull=True, student__agent=agent)
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
def choose_agent(request):
    agents = available_agents(request.user)
    if not agents.exists():
        raise PermissionDenied("An active agent membership is required.")
    active_agent = resolve_active_agent(request, required=False)
    if active_agent is not None:
        return redirect("agent-dashboard")
    return render(
        request,
        "agents/choose_agent.html",
        {"available_agent_workspaces": agents},
    )


@login_required
@require_POST
def switch_agent(request):
    agent_id = request.POST.get("agent_id", "")
    switch_active_agent(request, agent_id)
    next_url = request.POST.get("next", "")
    if next_url.startswith("/agent/") and not next_url.startswith("//"):
        try:
            match = resolve(next_url)
        except Resolver404:
            match = None
        if match is not None and match.url_name in {
            "agent-dashboard",
            "agent-applicant-list",
            "agent-application-list",
            "agent-message-inbox",
        }:
            return redirect(next_url)
    return redirect("agent-dashboard")


@login_required
def dashboard(request):
    if resolve_active_agent(request, required=False) is None:
        if available_agents(request.user).exists():
            return redirect("agent-choose")
        raise PermissionDenied("An active agent membership is required.")

    leads = _agent_leads(request)
    applications = _agent_applications(request)

    active_agent = _active_agent(request)
    unread_message_count = agent_unread_count(request.user, agent=active_agent)
    recent_messages = (
        Message.objects.filter(
            conversation__agent=active_agent,
            sender_role=MessageSenderRole.CUSTOMER,
        )
        .select_related("conversation", "conversation__subject_content_type", "sender")
        .order_by("-created_at")[:8]
    )
    program_requests = LeadProgramInterest.objects.filter(
        lead__in=leads,
        source="user",
    )

    today = timezone.localdate()
    active_todos = Todo.objects.filter(agent=active_agent).exclude(
        status__in=(TodoStatus.DONE, TodoStatus.CANCELLED)
    )
    recent_communications = CommunicationLog.objects.filter(agent=active_agent).select_related(
        "performed_by", "subject_content_type"
    )[:6]

    context = {
        "todo_overdue_count": active_todos.filter(due_date__lt=today).count(),
        "todo_due_today_count": active_todos.filter(due_date=today).count(),
        "todo_upcoming_count": active_todos.filter(due_date__gt=today).count(),
        "my_todos": active_todos.filter(assignee=request.user).order_by("due_date", "-created_at")[
            :6
        ],
        "recent_communications": recent_communications,
        "lead_count": leads.count(),
        "new_lead_count": leads.filter(status=LeadStatus.NEW).count(),
        "assigned_lead_count": leads.filter(status=LeadStatus.ASSIGNED).count(),
        "recommendation_count": leads.filter(needs_program_recommendation=True)
        .exclude(status__in=(LeadStatus.FINALIZED, LeadStatus.CLOSED))
        .count(),
        "unread_message_count": unread_message_count,
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
        "recent_messages": recent_messages,
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
    leads = _agent_leads(request).select_related("agent", "user", "assigned_to")
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


def _agent_applicant_context(*, request, lead, mark_read=False):
    conversation = ensure_conversation(lead)
    lead_messages = conversation.messages.select_related("sender").prefetch_related(
        "attachments__promoted_document"
    )
    if mark_read:
        mark_conversation_read(
            conversation=conversation,
            user=request.user,
            participant_role=ConversationParticipantRole.AGENT,
        )

    agent_users = (
        lead.agent.users.filter(is_active=True).order_by(
            "first_name", "last_name", "email", "username"
        )
        if lead.agent_id
        else []
    )
    interests = lead.program_interests.select_related(
        "program",
        "program__university",
        "program_offering",
    ).order_by("-created_at")
    student = lead.converted_student
    applications = (
        student.applications.select_related(
            "program_offering__program",
            "program_offering__program__university",
        ).order_by("-updated_at")
        if student is not None
        else []
    )
    program_search_query = (request.GET.get("program_q") or "").strip()
    program_search_results = Program.objects.none()
    if program_search_query:
        program_search_results = (
            Program.objects.filter(
                Q(name_en__icontains=program_search_query)
                | Q(university__name_en__icontains=program_search_query),
                is_active=True,
                university__is_active=True,
            )
            .select_related("university", "academic_unit")
            .prefetch_related("instruction_language_rows__language")
            .order_by("-listing_priority", "university__name_en", "name_en")[:20]
        )

    contextual_todos = todos_for_subject_tree(agent=lead.agent, subject=lead).select_related(
        "assignee", "subject_content_type"
    )
    contextual_communications = communications_for_subject_tree(
        agent=lead.agent,
        subject=lead,
    ).select_related("performed_by", "subject_content_type")

    return {
        "contextual_todos": contextual_todos,
        "contextual_communications": contextual_communications,
        "today": timezone.localdate(),
        "todo_form": TodoForm(agent=lead.agent),
        "communication_form": CommunicationLogForm(),
        "lead": lead,
        "agent_users": agent_users,
        "lead_messages": lead_messages,
        "conversation": conversation,
        "message_form": MessageForm(),
        "lead_edit_form": AgentLeadEditForm(instance=lead),
        "document_upload_form": AgentLeadDocumentUploadForm(),
        "document_review_form": DocumentReviewForm(),
        "promote_attachment_form": PromoteChatAttachmentForm(),
        "documents": lead.documents.select_related(
            "reviewed_by",
            "source_message_attachment",
        ).order_by("-created_at"),
        "interests": interests,
        "applications": applications,
        "program_search_query": program_search_query,
        "program_search_results": program_search_results,
        "program_interest_count": lead.program_interests.count(),
        "document_count": lead.documents.count(),
        "application_count": (student.applications.count() if student is not None else 0),
        "activities": lead.activities.select_related("created_by").order_by("-created_at")[:50],
        "status_choices": LeadStatus.choices,
        "agent_context": True,
        "applicant_unread_count": unread_count_for_conversation(
            conversation=conversation,
            user=request.user,
            participant_role=ConversationParticipantRole.AGENT,
        ),
    }


@login_required
def applicant_detail(request, lead_id):
    lead = (
        _agent_leads(request)
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
    context = _agent_applicant_context(request=request, lead=lead, mark_read=True)
    context["entity_tab"] = "overview"
    return render(request, "agents/applicant_detail.html", context)


@login_required
def applicant_section(request, lead_id, section):
    if section not in {
        "profile",
        "programs",
        "documents",
        "applications",
        "messages",
        "todos",
        "communications",
    }:
        raise PermissionDenied("Unknown applicant section.")
    lead = (
        _agent_leads(request)
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
    context = _agent_applicant_context(
        request=request,
        lead=lead,
        mark_read=section == "messages",
    )
    context["entity_tab"] = section
    return render(request, "agents/applicant_section.html", context)


@login_required
@require_POST
def applicant_recommend_program(request, lead_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(
            request,
            _(
                "Program recommendations cannot be changed after the applicant is "
                "finalized or closed."
            ),
        )
        return redirect("agent-applicant-programs", lead_id=lead.pk)

    program = get_object_or_404(
        Program.objects.select_related("university"),
        pk=request.POST.get("program_id"),
        is_active=True,
        university__is_active=True,
    )
    reason = (request.POST.get("suggestion_reason") or "").strip()

    result = recommend_program(
        lead=lead,
        program=program,
        agent_user=request.user,
        reason=reason,
    )
    if result.outcome == RecommendationOutcome.USER_INTEREST_EXISTS:
        messages.info(request, _("This program is already on the applicant's list."))
    elif result.outcome == RecommendationOutcome.UPDATED:
        messages.success(request, _("Recommendation updated."))
    elif result.outcome == RecommendationOutcome.ALREADY_RECOMMENDED:
        messages.info(request, _("This program is already recommended."))
    else:
        messages.success(request, _("Program recommended to applicant."))
    return redirect("agent-applicant-programs", lead_id=lead.pk)


@login_required
@require_POST
def applicant_remove_recommendation(request, lead_id, interest_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(
            request,
            _(
                "Program recommendations cannot be changed after the applicant is "
                "finalized or closed."
            ),
        )
        return redirect("agent-applicant-programs", lead_id=lead.pk)

    interest = get_object_or_404(
        lead.program_interests.select_related("program"),
        pk=interest_id,
        source="agent",
    )
    program_name = interest.program.localized_name
    interest.delete()
    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.PROGRAM_RESPONSE,
        description=f"Program recommendation removed: {program_name}.",
        metadata={"action": "recommendation_removed"},
        is_customer_visible=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Program recommendation removed."))
    return redirect("agent-applicant-programs", lead_id=lead.pk)


@login_required
def applicant_activity(request, lead_id):
    lead = (
        _agent_leads(request)
        .select_related("agent", "user", "assigned_to")
        .filter(pk=lead_id)
        .first()
    )
    if lead is None:
        return _render_agent_not_found(
            request,
            resource_name="applicant",
            list_url_name="agent-applicant-list",
        )

    activity_filter = (request.GET.get("type") or "all").strip()
    page_number = request.GET.get("page") or "1"

    filter_map = {
        "applicant": (LeadActivityType.APPLICANT_UPDATED,),
        "notes": (
            LeadActivityType.NOTE,
            LeadActivityType.INTERNAL_NOTES_UPDATED,
        ),
        "documents": (
            LeadActivityType.DOCUMENT_UPLOADED,
            LeadActivityType.DOCUMENT_REVIEWED,
        ),
        "assignment": (
            LeadActivityType.ASSIGNED,
            LeadActivityType.REASSIGNED,
            LeadActivityType.STATUS_CHANGED,
            LeadActivityType.CLOSED,
            LeadActivityType.REOPENED,
            LeadActivityType.FINALIZED,
            LeadActivityType.VALIDATED,
        ),
        "programs": (
            LeadActivityType.PROGRAM_ADDED,
            LeadActivityType.PROGRAM_SUGGESTED,
            LeadActivityType.PROGRAM_RESPONSE,
            LeadActivityType.RECOMMENDATIONS_GENERATED,
        ),
    }

    activities = lead.activities.select_related("created_by").order_by("-created_at")
    if activity_filter in filter_map:
        activities = activities.filter(activity_type__in=filter_map[activity_filter])
    else:
        activity_filter = "all"

    paginator = Paginator(activities, 25)
    activity_page = paginator.get_page(page_number)

    return render(
        request,
        "agents/applicant_activity.html",
        {
            "lead": lead,
            "activities": activity_page.object_list,
            "activity_page": activity_page,
            "activity_filter": activity_filter,
        },
    )


@login_required
@require_POST
def applicant_internal_notes(request, lead_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.converted_student_id:
        messages.error(
            request,
            _("Internal Lead notes are read-only after Student creation."),
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    new_notes = request.POST.get("notes", "")
    old_notes = lead.notes
    if new_notes == old_notes:
        messages.info(request, _("Internal notes were not changed."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    lead.notes = new_notes
    lead.updated_by = request.user
    lead.save(update_fields=("notes", "updated_by", "updated_at"))

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.INTERNAL_NOTES_UPDATED,
        description="Internal notes updated.",
        metadata={
            "changes": [
                {
                    "field": "notes",
                    "label": "Internal notes",
                    "old": old_notes or "—",
                    "new": new_notes or "—",
                }
            ]
        },
        is_customer_visible=False,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Internal notes updated."))
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
def applicant_edit(request, lead_id):
    lead = (
        _agent_leads(request)
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
    if lead.converted_student_id or lead.status == LeadStatus.CLOSED:
        messages.error(
            request,
            _("Student-linked or closed applicant data cannot be edited here."),
        )
        return redirect("agent-applicant-profile", lead_id=lead.pk)

    form = AgentLeadEditForm(
        request.POST if request.method == "POST" else None,
        instance=lead,
    )
    if request.method == "POST" and form.is_valid():
        updated_lead = form.save(commit=False)
        updated_lead.updated_by = request.user
        updated_lead.save()

        if record_applicant_profile_update(
            lead=updated_lead,
            form=form,
            actor=request.user,
        ):
            messages.success(request, _("Applicant data updated."))
        else:
            messages.info(request, _("No applicant data changed."))
        return redirect("agent-applicant-profile", lead_id=lead.pk)

    return render(
        request,
        "agents/applicant_edit.html",
        {
            "lead": lead,
            "form": form,
            "entity_tab": "profile",
            "agent_context": True,
        },
    )


@login_required
@require_POST
def applicant_document_upload(request, lead_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.converted_student_id:
        messages.error(
            request,
            _("Upload documents to the Student record after finalization."),
        )
        return redirect("agent-applicant-documents", lead_id=lead.pk)

    form = AgentLeadDocumentUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        detail = " ".join(
            str(message) for field_messages in form.errors.values() for message in field_messages
        )
        messages.error(
            request,
            _("Document was not uploaded. %(detail)s") % {"detail": detail},
        )
        return redirect("agent-applicant-documents", lead_id=lead.pk)

    document = form.save(commit=False)
    document.lead = lead
    document.review_status = LeadDocumentReviewStatus.APPROVED
    document.reviewed_by = request.user
    document.reviewed_at = timezone.now()
    document.is_verified = True
    document.created_by = request.user
    document.updated_by = request.user
    document.save()

    LeadDocumentReviewHistory.objects.create(
        document=document,
        review_status=LeadDocumentReviewStatus.APPROVED,
        review_note="Uploaded directly by agent user.",
        reviewed_by=request.user,
        reviewed_at=document.reviewed_at,
        created_by=request.user,
        updated_by=request.user,
    )

    LeadActivity.objects.create(
        lead=lead,
        activity_type=LeadActivityType.DOCUMENT_UPLOADED,
        description=(
            f"{document.get_document_type_display()} uploaded and approved by agent user."
        ),
        is_customer_visible=False,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Document uploaded and approved."))
    return redirect("agent-applicant-documents", lead_id=lead.pk)


@login_required
@require_POST
def applicant_status(request, lead_id):
    """Only closing/reopening is manually controlled; other statuses are derived."""
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    action = (request.POST.get("action") or "").strip()

    if action == "close":
        if lead.status == LeadStatus.FINALIZED:
            messages.error(request, _("A finalized applicant cannot be closed."))
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
        messages.success(request, _("Applicant closed."))
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
        messages.success(request, _("Applicant reopened."))
    else:
        messages.error(request, _("Invalid applicant status action."))

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
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(request, _("This applicant can no longer be assigned."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if lead.assigned_to_id == request.user.pk:
        messages.info(request, _("You are already responsible for this applicant."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if not lead.agent_id or not lead.agent.users.filter(pk=request.user.pk).exists():
        messages.error(request, _("You are not an active user of this applicant's agent."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    _assign_lead(
        lead,
        target_user=request.user,
        performed_by=request.user,
    )
    messages.success(request, _("You are now responsible for this applicant."))
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_assign(request, lead_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    if lead.status in {LeadStatus.FINALIZED, LeadStatus.CLOSED}:
        messages.error(request, _("This applicant can no longer be assigned."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    user_id = (request.POST.get("user_id") or "").strip()
    if not user_id or not lead.agent_id:
        messages.error(request, _("Choose a responsible agent user."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    target_user = lead.agent.users.filter(
        pk=user_id,
        is_active=True,
    ).first()
    if target_user is None:
        messages.error(
            request,
            _("The selected user does not belong to this applicant's agent."),
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    if lead.assigned_to_id == target_user.pk:
        messages.info(request, _("This user is already responsible for the applicant."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    _assign_lead(
        lead,
        target_user=target_user,
        performed_by=request.user,
    )
    messages.success(
        request,
        _("%(user)s is now responsible for this applicant.")
        % {"user": _user_display_name(target_user)},
    )
    return redirect("agent-applicant-detail", lead_id=lead.pk)


def _student_conversion_initial(lead: Lead) -> dict[str, object]:
    fields = StudentRecordConversionForm.Meta.fields
    return {field: getattr(lead, field) for field in fields}


def _student_conversion_programs(lead: Lead, request) -> list[dict[str, object]]:
    selected_ids = (
        set(request.POST.getlist("program_interest")) if request.method == "POST" else set()
    )
    existing_active_offering_ids: set[object] = set()
    converted_student = lead.converted_student
    if converted_student is not None:
        existing_active_offering_ids = set(
            converted_student.applications.exclude(
                status__in=(
                    ApplicationStatus.REJECTED,
                    ApplicationStatus.WITHDRAWN,
                    ApplicationStatus.CANCELLED,
                )
            ).values_list("program_offering_id", flat=True)
        )
    rows: list[dict[str, object]] = []
    interests = lead.program_interests.select_related(
        "program",
        "program__university",
        "program_offering",
    ).order_by("-created_at")
    for interest in interests:
        offerings = list(
            ProgramOffering.objects.filter(program=interest.program, is_active=True)
            .select_related("academic_year", "intake")
            .order_by("academic_year__name_en", "intake__name_en")
        )
        selected_offering_id = ""
        if request.method == "POST":
            selected_offering_id = request.POST.get(f"offering_{interest.pk}", "")
        elif interest.program_offering is not None and interest.program_offering.is_active:
            selected_offering_id = str(interest.program_offering_id)
        already_applied = (
            interest.program_offering_id in existing_active_offering_ids
            if interest.program_offering_id
            else False
        )
        rows.append(
            {
                "interest": interest,
                "offerings": offerings,
                "selected": (
                    str(interest.pk) in selected_ids
                    if request.method == "POST"
                    else bool(selected_offering_id) and not already_applied
                ),
                "selected_offering_id": str(selected_offering_id),
                "already_applied": already_applied,
            }
        )
    return rows


@login_required
def applicant_finalize(request, lead_id):
    lead = (
        _agent_leads(request)
        .select_related("agent", "user", "assigned_to", "converted_student")
        .filter(pk=lead_id)
        .first()
    )
    if lead is None:
        return _render_agent_not_found(
            request,
            resource_name="applicant",
            list_url_name="agent-applicant-list",
        )
    if lead.status == LeadStatus.CLOSED:
        messages.error(request, _("Reopen this applicant before creating a Student record."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)
    if lead.status == LeadStatus.FINALIZED:
        messages.info(request, _("This applicant already has a Student record."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)
    if lead.assigned_to_id != request.user.pk:
        messages.error(
            request,
            _("Assign this applicant to yourself before creating a Student record."),
        )
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    is_reopened = lead.status == LeadStatus.REOPENED and bool(lead.converted_student_id)
    form = StudentRecordConversionForm(
        request.POST if request.method == "POST" and not is_reopened else None,
        initial=_student_conversion_initial(lead),
    )
    documents = (
        []
        if is_reopened
        else list(lead.documents.select_related("reviewed_by").order_by("-created_at"))
    )
    selected_document_ids = (
        set()
        if is_reopened
        else (
            set(request.POST.getlist("document"))
            if request.method == "POST"
            else {str(document.pk) for document in documents if document.is_verified}
        )
    )
    program_rows = _student_conversion_programs(lead, request)

    if request.method == "POST" and (is_reopened or form.is_valid()):
        errors: list[str] = []
        selections: list[tuple[LeadProgramInterest, ProgramOffering]] = []
        selected_interest_ids = set(request.POST.getlist("program_interest"))
        selected_interests = lead.program_interests.select_related("program").filter(
            pk__in=selected_interest_ids
        )
        interests_by_id: dict[str, LeadProgramInterest] = {
            str(interest.pk): interest for interest in selected_interests
        }

        for interest_id in selected_interest_ids:
            interest = interests_by_id.get(interest_id)
            if interest is None:
                errors.append("One or more selected discussed programs are invalid.")
                continue
            offering_id = request.POST.get(f"offering_{interest.pk}")
            if not offering_id:
                errors.append(f"Choose an offering for {interest.program}.")
                continue
            offering = ProgramOffering.objects.filter(
                pk=offering_id,
                program=interest.program,
                is_active=True,
            ).first()
            if offering is None:
                errors.append(f"Choose a valid active offering for {interest.program}.")
                continue
            selections.append((interest, offering))

        valid_document_ids = {str(document.pk) for document in documents}
        if not selected_document_ids.issubset(valid_document_ids):
            errors.append("One or more selected documents are invalid.")

        if not errors:
            try:
                student = finalize_lead(
                    lead,
                    student_data=None if is_reopened else form.cleaned_data,
                    selected_document_ids=(None if is_reopened else list(selected_document_ids)),
                    application_selections=selections,
                    performed_by=request.user,
                )
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for field, field_messages in exc.message_dict.items():
                        if field in form.fields:
                            for message in field_messages:
                                form.add_error(field, message)
                        else:
                            for message in field_messages:
                                form.add_error(None, message)
                else:
                    for message in exc.messages:
                        form.add_error(None, message)
            else:
                if is_reopened:
                    messages.success(
                        request,
                        _("Reopened Request completed for %(student)s.") % {"student": student},
                    )
                else:
                    messages.success(
                        request,
                        _(
                            "Student record created for %(student)s. Transferred "
                            "%(documents)s document(s) and created %(applications)s "
                            "draft application(s)."
                        )
                        % {
                            "student": student,
                            "documents": len(selected_document_ids),
                            "applications": len(selections),
                        },
                    )
                return redirect("agent-student-detail", student_id=student.pk)
        else:
            for error in errors:
                form.add_error(None, error)

    return render(
        request,
        "agents/student_record_create.html",
        {
            "lead": lead,
            "form": form,
            "documents": documents,
            "selected_document_ids": selected_document_ids,
            "program_rows": program_rows,
            "selected_document_count": len(selected_document_ids),
            "is_reopened": is_reopened,
            "agent_context": True,
        },
    )


@login_required
@require_POST
def applicant_message(request, lead_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    conversation = ensure_conversation(lead)
    if conversation.is_closed:
        messages.error(request, _("This conversation is closed."))
        return redirect("agent-applicant-messages", lead_id=lead.pk)

    form = MessageForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, _("Write a message or attach a file."))
        return redirect("agent-applicant-messages", lead_id=lead.pk)

    send_message(
        conversation=conversation,
        sender=request.user,
        sender_role=MessageSenderRole.AGENT,
        body=form.cleaned_data.get("body", ""),
        attachment=form.cleaned_data.get("attachment"),
    )
    return redirect("agent-applicant-messages", lead_id=lead.pk)


@login_required
@require_POST
def applicant_document_review(request, lead_id, document_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    document = get_object_or_404(LeadDocument, pk=document_id, lead=lead)
    form = DocumentReviewForm(request.POST)

    if not form.is_valid():
        messages.error(request, _("Choose a valid document review decision."))
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
        send_system_message(
            lead,
            event_type=SystemMessageEventType.DOCUMENT_REPLACEMENT_REQUESTED,
            event_data={
                "document_type": document.document_type,
                "reason": reason,
            },
            performed_by=request.user,
        )

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
    messages.success(request, _("Document review updated."))
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
@require_POST
def applicant_attachment_to_document(request, lead_id, attachment_id):
    lead = get_object_or_404(_agent_leads(request), pk=lead_id)
    attachment = get_object_or_404(
        MessageAttachment.objects.select_related(
            "message",
            "message__conversation",
            "message__conversation__subject_content_type",
        ),
        pk=attachment_id,
        message__sender_role=MessageSenderRole.CUSTOMER,
    )
    if attachment.message.conversation.subject != lead:
        raise PermissionDenied("Attachment does not belong to this applicant.")

    if hasattr(attachment, "promoted_document"):
        messages.info(request, _("This attachment is already in Documents."))
        return redirect("agent-applicant-detail", lead_id=lead.pk)

    form = PromoteChatAttachmentForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Choose a document type before adding the attachment."))
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
    messages.success(request, _("Attachment added to Documents and marked for review."))
    return redirect("agent-applicant-detail", lead_id=lead.pk)


@login_required
def message_inbox(request):
    active_agent = _active_agent(request)
    conversations = (
        Conversation.objects.filter(agent=active_agent)
        .select_related("agent", "customer", "subject_content_type")
        .distinct()
        .order_by("-updated_at")
    )
    rows = []
    for conversation in conversations:
        latest = conversation.messages.select_related("sender").order_by("-created_at").first()
        rows.append(
            {
                "conversation": conversation,
                "latest_message": latest,
                "unread_count": unread_count_for_conversation(
                    conversation=conversation,
                    user=request.user,
                    participant_role=ConversationParticipantRole.AGENT,
                ),
            }
        )
    return render(request, "agents/message_inbox.html", {"conversation_rows": rows})


@login_required
def student_detail(request, student_id):
    student = (
        _agent_students(request)
        .select_related("agent", "user", "source_lead")
        .filter(pk=student_id)
        .first()
    )
    if student is None:
        return _render_agent_not_found(
            request,
            resource_name="student",
            list_url_name="agent-application-list",
        )

    source_lead = getattr(student, "source_lead", None)
    discussed_programs = (
        source_lead.program_interests.select_related(
            "program",
            "program__university",
            "program_offering",
            "program_offering__academic_year",
            "program_offering__intake",
        ).order_by("-created_at")
        if source_lead is not None
        else []
    )

    applications = student.applications.select_related(
        "program_offering",
        "program_offering__program",
        "program_offering__program__university",
        "program_offering__academic_year",
        "program_offering__intake",
    ).order_by("-updated_at")

    student_conversation = get_or_create_conversation(subject=student)
    student_messages = student_conversation.messages.select_related("sender").prefetch_related(
        "attachments"
    )
    mark_conversation_read(
        conversation=student_conversation,
        user=request.user,
        participant_role=ConversationParticipantRole.AGENT,
    )

    return render(
        request,
        "agents/student_detail.html",
        {
            "student": student,
            "source_lead": source_lead,
            "discussed_programs": discussed_programs,
            "applications": applications,
            "new_application_form": StudentApplicationOfferingForm(),
            "student_document_form": StudentDocumentUploadForm(),
            "conversation": student_conversation,
            "student_messages": student_messages,
            "message_form": MessageForm(),
        },
    )


@login_required
@require_POST
def student_document_upload(request, student_id):
    student = get_object_or_404(_agent_students(request), pk=student_id)
    form = StudentDocumentUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, _("Could not upload document. Check the supplied fields."))
        return redirect("agent-student-detail", student_id=student.pk)

    document = form.save(commit=False)
    document.student = student
    document.created_by = request.user
    document.updated_by = request.user
    document.save()
    messages.success(request, _("Student document uploaded."))
    return redirect("agent-student-detail", student_id=student.pk)


@login_required
@require_POST
def student_new_application(request, student_id):
    student = get_object_or_404(_agent_students(request), pk=student_id)
    form = StudentApplicationOfferingForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Choose a valid program intake."))
        return redirect("agent-student-detail", student_id=student.pk)

    try:
        application = create_student_application(
            student=student,
            offering=form.cleaned_data["offering"],
            performed_by=request.user,
        )
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("agent-student-detail", student_id=student.pk)

    messages.success(request, _("Draft application created."))
    return redirect("agent-application-detail", application_id=application.pk)


@login_required
@require_POST
def student_start_discussed_application(request, student_id, interest_id):
    student = get_object_or_404(_agent_students(request), pk=student_id)
    source_lead = getattr(student, "source_lead", None)
    if source_lead is None:
        messages.error(request, _("This student has no originating applicant record."))
        return redirect("agent-student-detail", student_id=student.pk)

    interest = get_object_or_404(
        source_lead.program_interests.select_related(
            "program",
            "program_offering",
        ),
        pk=interest_id,
    )

    if interest.program_offering_id:
        offering = interest.program_offering
    else:
        form = StudentApplicationOfferingForm(request.POST, program=interest.program)
        if not form.is_valid():
            messages.error(
                request,
                _("Choose a valid intake for the discussed program."),
            )
            return redirect("agent-student-detail", student_id=student.pk)
        offering = form.cleaned_data["offering"]

    try:
        application = create_student_application(
            student=student,
            offering=offering,
            performed_by=request.user,
        )
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("agent-student-detail", student_id=student.pk)

    messages.success(request, _("Discussed program converted to a draft application."))
    return redirect("agent-application-detail", application_id=application.pk)


@login_required
@require_POST
def student_message(request, student_id):
    student = get_object_or_404(_agent_students(request), pk=student_id)
    conversation = get_or_create_conversation(subject=student)
    form = MessageForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, _("Write a message or attach a file."))
        return redirect("agent-student-detail", student_id=student.pk)
    send_message(
        conversation=conversation,
        sender=request.user,
        sender_role=MessageSenderRole.AGENT,
        body=form.cleaned_data.get("body", ""),
        attachment=form.cleaned_data.get("attachment"),
    )
    return redirect("agent-student-detail", student_id=student.pk)


@login_required
@require_POST
def application_message(request, application_id):
    application = get_object_or_404(_agent_applications(request), pk=application_id)
    conversation = get_or_create_conversation(subject=application)
    form = MessageForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, _("Write a message or attach a file."))
        return redirect("agent-application-messages", application_id=application.pk)
    send_message(
        conversation=conversation,
        sender=request.user,
        sender_role=MessageSenderRole.AGENT,
        body=form.cleaned_data.get("body", ""),
        attachment=form.cleaned_data.get("attachment"),
    )
    return redirect("agent-application-messages", application_id=application.pk)


@login_required
def application_list(request):
    leads = _agent_leads(request)
    program_requests = LeadProgramInterest.objects.filter(
        lead__in=leads,
        source="user",
    ).select_related(
        "lead",
        "program",
        "program__university",
        "program_offering",
    )
    applications = _agent_applications(request).select_related(
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


def _agent_application_activity(application):
    events: list[dict[str, Any]] = [
        {
            "when": application.created_at,
            "title": _("Application created"),
            "detail": str(application.get_status_display()),
        },
    ]
    for document in application.documents.select_related("student_document").all():
        events.append(
            {
                "when": document.created_at,
                "title": _("Document added"),
                "detail": str(document.student_document.get_document_type_display()),
            }
        )
    conversation = get_or_create_conversation(subject=application)
    for message in conversation.messages.order_by("created_at")[:20]:
        events.append(
            {
                "when": message.created_at,
                "title": _("Message"),
                "detail": (
                    message.localized_body[:120] if message.localized_body else _("Attachment")
                ),
            }
        )
    application_agent = application.agent or application.student.agent
    for todo in todos_for_subject_tree(
        agent=application_agent,
        subject=application,
    ):
        events.append(
            {
                "when": todo.updated_at,
                "title": _("TODO"),
                "detail": f"{todo.title} · {todo.get_status_display()}",
            }
        )
    for communication in communications_for_subject_tree(
        agent=application_agent,
        subject=application,
    ):
        events.append(
            {
                "when": communication.occurred_at,
                "title": _("Communication Log"),
                "detail": (
                    f"{communication.get_channel_display()} · {communication.summary[:120]}"
                ),
            }
        )
    if application.updated_at != application.created_at:
        events.append(
            {
                "when": application.updated_at,
                "title": _("Application updated"),
                "detail": str(application.get_status_display()),
            }
        )
    return sorted(events, key=lambda event: event["when"], reverse=True)


def _agent_application_context(*, request, application, tab, mark_read=False):
    conversation = get_or_create_conversation(subject=application)
    if mark_read:
        mark_conversation_read(
            conversation=conversation,
            user=request.user,
            participant_role=ConversationParticipantRole.AGENT,
        )
    application_agent = application.agent or application.student.agent
    contextual_todos = todos_for_subject_tree(
        agent=application_agent,
        subject=application,
    ).select_related("assignee", "subject_content_type")
    contextual_communications = communications_for_subject_tree(
        agent=application_agent,
        subject=application,
    ).select_related("performed_by", "subject_content_type")

    return {
        "contextual_todos": contextual_todos,
        "contextual_communications": contextual_communications,
        "today": timezone.localdate(),
        "todo_form": TodoForm(agent=application_agent),
        "communication_form": CommunicationLogForm(),
        "application": application,
        "source_lead": getattr(application.student, "source_lead", None),
        "status_choices": ApplicationStatus.choices,
        "existing_document_form": ApplicationExistingDocumentForm(
            student=application.student,
            application=application,
        ),
        "application_document_upload_form": ApplicationDocumentUploadForm(),
        "conversation": conversation,
        "application_messages": conversation.messages.select_related("sender").prefetch_related(
            "attachments"
        ),
        "message_form": MessageForm(),
        "requirements": application.documents.select_related("student_document").filter(
            is_required=True
        ),
        "activity_events": _agent_application_activity(application),
        "entity_tab": tab,
        "agent_context": True,
    }


@login_required
def application_detail(request, application_id):
    application = (
        _agent_applications(request)
        .select_related(
            "student",
            "student__source_lead",
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
    context = _agent_application_context(
        request=request,
        application=application,
        tab="overview",
        mark_read=True,
    )
    return render(request, "agents/application_detail.html", context)


@login_required
def application_section(request, application_id, section):
    if section not in {
        "requirements",
        "documents",
        "activity",
        "messages",
        "todos",
        "communications",
    }:
        raise PermissionDenied("Unknown application section.")
    application = (
        _agent_applications(request)
        .select_related(
            "student",
            "student__source_lead",
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
    context = _agent_application_context(
        request=request,
        application=application,
        tab=section,
        mark_read=section == "messages",
    )
    return render(request, "agents/application_section.html", context)


@login_required
@require_POST
def application_add_existing_document(request, application_id):
    application = get_object_or_404(
        _agent_applications(request).select_related("student"),
        pk=application_id,
    )
    form = ApplicationExistingDocumentForm(
        request.POST,
        student=application.student,
        application=application,
    )
    if not form.is_valid():
        messages.error(request, _("Choose an available student document."))
        return redirect("agent-application-documents", application_id=application.pk)

    ApplicationDocument.objects.create(
        application=application,
        student_document=form.cleaned_data["student_document"],
        is_verified=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Student document added to application."))
    return redirect("agent-application-documents", application_id=application.pk)


@login_required
@require_POST
def application_upload_document(request, application_id):
    application = get_object_or_404(
        _agent_applications(request).select_related("student"),
        pk=application_id,
    )
    form = ApplicationDocumentUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, _("Could not upload document. Check the supplied fields."))
        return redirect("agent-application-documents", application_id=application.pk)

    student_document = form.save(commit=False)
    student_document.student = application.student
    student_document.created_by = request.user
    student_document.updated_by = request.user
    student_document.save()

    ApplicationDocument.objects.create(
        application=application,
        student_document=student_document,
        is_verified=True,
        created_by=request.user,
        updated_by=request.user,
    )
    messages.success(request, _("Document uploaded and added to application."))
    return redirect("agent-application-documents", application_id=application.pk)


@login_required
@require_POST
def application_status(request, application_id):
    application = get_object_or_404(
        _agent_applications(request),
        pk=application_id,
    )
    status = request.POST.get("status")
    if status not in ApplicationStatus.values:
        messages.error(request, _("Invalid application status."))
        return redirect("agent-application-detail", application_id=application.pk)

    application.status = status
    application.updated_by = request.user
    application.save(update_fields=("status", "updated_by", "updated_at"))
    messages.success(request, _("Application status updated."))
    return redirect("agent-application-detail", application_id=application.pk)


def _operation_subject(request, subject_kind, subject_id):
    if not subject_kind or not subject_id:
        return None
    if subject_kind == "applicant":
        return get_object_or_404(_agent_leads(request), pk=subject_id)
    if subject_kind == "application":
        return get_object_or_404(
            _agent_applications(request).select_related("student", "student__source_lead"),
            pk=subject_id,
        )
    raise PermissionDenied("Unsupported operation subject.")


def _operation_redirect(subject):
    if isinstance(subject, Lead):
        return redirect("agent-applicant-todos", lead_id=subject.pk)
    if isinstance(subject, Application):
        return redirect("agent-application-todos", application_id=subject.pk)
    return redirect("agent-todo-list")


def _communication_redirect(subject):
    if isinstance(subject, Lead):
        return redirect("agent-applicant-communications", lead_id=subject.pk)
    if isinstance(subject, Application):
        return redirect(
            "agent-application-communications",
            application_id=subject.pk,
        )
    return redirect("agent-communication-list")


@login_required
def todo_list(request):
    agent = _active_agent(request)
    todos = Todo.objects.filter(agent=agent).select_related(
        "assignee", "created_by", "subject_content_type"
    )
    status = (request.GET.get("status") or "").strip()
    if status in TodoStatus.values:
        todos = todos.filter(status=status)
    today = timezone.localdate()
    return render(
        request,
        "agents/todo_list.html",
        {
            "todos": todos,
            "contextual_todos": todos,
            "todo_form": TodoForm(agent=agent),
            "status_choices": TodoStatus.choices,
            "selected_status": status,
            "today": today,
        },
    )


@login_required
@require_POST
def todo_create(request):
    agent = _active_agent(request)
    subject = _operation_subject(
        request,
        (request.POST.get("subject_kind") or "").strip(),
        (request.POST.get("subject_id") or "").strip(),
    )
    form = TodoForm(request.POST, agent=agent)
    if not form.is_valid():
        messages.error(request, _("Could not create TODO. Check the supplied fields."))
        return _operation_redirect(subject)
    todo = create_todo(
        agent=agent,
        actor=request.user,
        title=form.cleaned_data["title"],
        description=form.cleaned_data["description"],
        due_date=form.cleaned_data["due_date"],
        assignee=form.cleaned_data["assignee"],
        subject=subject,
    )
    messages.success(
        request,
        _("TODO created: %(title)s.") % {"title": todo.title},
    )
    return _operation_redirect(subject)


@login_required
@require_POST
def todo_update(request, todo_id):
    todo = get_object_or_404(
        Todo.objects.select_related("subject_content_type"),
        pk=todo_id,
        agent=_active_agent(request),
    )
    status = (request.POST.get("status") or "").strip() or None
    assignee_marker = "assignee" in request.POST
    assignee = None
    if assignee_marker and request.POST.get("assignee"):
        assignee = get_object_or_404(
            todo.agent.users.filter(is_active=True),
            pk=request.POST["assignee"],
        )
    update_todo(
        todo=todo,
        actor=request.user,
        status=status,
        assignee_marker=assignee_marker,
        assignee=assignee,
    )
    messages.success(request, _("TODO updated."))
    return _operation_redirect(todo.subject)


@login_required
@require_POST
def todo_comment(request, todo_id):
    todo = get_object_or_404(
        Todo.objects.select_related("subject_content_type"),
        pk=todo_id,
        agent=_active_agent(request),
    )
    body = (request.POST.get("body") or "").strip()
    if not body:
        messages.error(request, _("Comment cannot be empty."))
    else:
        add_todo_comment(todo=todo, actor=request.user, body=body)
        messages.success(request, _("Comment added."))
    return _operation_redirect(todo.subject)


@login_required
def communication_list(request):
    agent = _active_agent(request)
    communications = CommunicationLog.objects.filter(agent=agent).select_related(
        "performed_by", "created_by", "subject_content_type"
    )
    return render(
        request,
        "agents/communication_list.html",
        {
            "communications": communications,
            "contextual_communications": communications,
            "communication_form": CommunicationLogForm(),
        },
    )


@login_required
@require_POST
def communication_create(request):
    agent = _active_agent(request)
    subject = _operation_subject(
        request,
        (request.POST.get("subject_kind") or "").strip(),
        (request.POST.get("subject_id") or "").strip(),
    )
    form = CommunicationLogForm(request.POST)
    if not form.is_valid():
        messages.error(
            request,
            _("Could not record communication. Check the supplied fields."),
        )
        return _communication_redirect(subject)
    communication = create_communication(
        agent=agent,
        actor=request.user,
        subject=subject,
        **form.cleaned_data,
    )
    messages.success(
        request,
        _("%(channel)s communication recorded.") % {"channel": communication.get_channel_display()},
    )
    return _communication_redirect(subject)


@login_required
@require_POST
def communication_edit(request, communication_id):
    communication = get_object_or_404(
        CommunicationLog.objects.select_related("subject_content_type"),
        pk=communication_id,
        agent=_active_agent(request),
    )
    form = CommunicationLogForm(request.POST)
    if not form.is_valid():
        messages.error(request, _("Could not update communication."))
        return _communication_redirect(communication.subject)
    edit_communication(
        communication=communication,
        actor=request.user,
        values=form.cleaned_data,
    )
    messages.success(request, _("Communication updated; previous version retained."))
    return _communication_redirect(communication.subject)


@login_required
@require_POST
def communication_create_todo(request, communication_id):
    communication = get_object_or_404(
        CommunicationLog.objects.select_related("subject_content_type"),
        pk=communication_id,
        agent=_active_agent(request),
    )
    title = (request.POST.get("title") or "").strip()
    if not title:
        title = _("Follow up: %(channel)s communication") % {
            "channel": communication.get_channel_display()
        }
    todo = create_todo(
        agent=communication.agent,
        actor=request.user,
        title=title,
        description=communication.summary,
        subject=communication.subject,
    )
    messages.success(
        request,
        _("TODO created: %(title)s.") % {"title": todo.title},
    )
    return _communication_redirect(communication.subject)
