from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.messaging.forms import MessageForm
from apps.messaging.models import ConversationParticipantRole, MessageSenderRole
from apps.messaging.services import get_or_create_conversation, mark_conversation_read, send_message

from .models import Application


def _customer_application(user, application_id):
    return get_object_or_404(
        Application.objects.select_related(
            "student",
            "student__source_lead",
            "agent",
            "program_offering__program",
            "program_offering__program__university",
            "program_offering__academic_year",
            "program_offering__intake",
        ).prefetch_related("documents__student_document"),
        pk=application_id,
        student__user=user,
    )


def _application_activity(application):
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
    if application.updated_at != application.created_at:
        events.append(
            {
                "when": application.updated_at,
                "title": _("Application updated"),
                "detail": str(application.get_status_display()),
            }
        )
    return sorted(events, key=lambda event: event["when"], reverse=True)


def _application_context(*, request, application, tab, mark_read=False):
    conversation = get_or_create_conversation(subject=application)
    if mark_read:
        mark_conversation_read(
            conversation=conversation,
            user=request.user,
            participant_role=ConversationParticipantRole.CUSTOMER,
        )
    return {
        "application": application,
        "source_lead": getattr(application.student, "source_lead", None),
        "entity_tab": tab,
        "agent_context": False,
        "conversation": conversation,
        "application_messages": conversation.messages.select_related("sender").prefetch_related(
            "attachments"
        ),
        "message_form": MessageForm(),
        "requirements": application.documents.select_related("student_document").filter(
            is_required=True
        ),
        "activity_events": _application_activity(application),
    }


@login_required
def customer_application_detail(request, application_id):
    application = _customer_application(request.user, application_id)
    return render(
        request,
        "applications/customer_detail.html",
        _application_context(request=request, application=application, tab="overview"),
    )


@login_required
def customer_application_requirements(request, application_id):
    application = _customer_application(request.user, application_id)
    return render(
        request,
        "applications/customer_detail.html",
        _application_context(request=request, application=application, tab="requirements"),
    )


@login_required
def customer_application_documents(request, application_id):
    application = _customer_application(request.user, application_id)
    return render(
        request,
        "applications/customer_detail.html",
        _application_context(request=request, application=application, tab="documents"),
    )


@login_required
def customer_application_activity(request, application_id):
    application = _customer_application(request.user, application_id)
    return render(
        request,
        "applications/customer_detail.html",
        _application_context(request=request, application=application, tab="activity"),
    )


@login_required
def customer_application_messages(request, application_id):
    application = _customer_application(request.user, application_id)
    return render(
        request,
        "applications/customer_detail.html",
        _application_context(
            request=request,
            application=application,
            tab="messages",
            mark_read=True,
        ),
    )


@login_required
@require_POST
def customer_application_send_message(request, application_id):
    application = _customer_application(request.user, application_id)
    conversation = get_or_create_conversation(subject=application)
    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        send_message(
            conversation=conversation,
            sender=request.user,
            sender_role=MessageSenderRole.CUSTOMER,
            body=form.cleaned_data.get("body", ""),
            attachment=form.cleaned_data.get("attachment"),
        )
    return redirect("customer-application-messages", application_id=application.pk)
