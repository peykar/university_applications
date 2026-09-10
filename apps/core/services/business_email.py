from __future__ import annotations

import logging
from collections.abc import Iterable

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import translation

from .business_email_content import BusinessEmailContent, build_business_email_content
from .emailing import send_email

logger = logging.getLogger(__name__)


def _url(path: str) -> str:
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def _name(user) -> str:
    return (user.get_full_name() or user.get_username() or user.email).strip()


def _send(*, email_type: str, recipient, content: BusinessEmailContent) -> None:
    email = getattr(recipient, "email", "")
    if not email:
        return
    send_email(
        email_type=email_type,
        subject=content.subject,
        to=email,
        text_body=content.text_body,
    )


def _after_commit(callback) -> None:
    def safe_callback():
        try:
            callback()
        except Exception:
            logger.exception("Business email delivery failed after domain commit.")

    transaction.on_commit(safe_callback)


def notify_request_created(lead) -> None:
    def deliver():
        with translation.override(translation.get_language() or settings.LANGUAGE_CODE):
            customer_url = _url(reverse("lead-detail", kwargs={"lead_id": lead.pk}))
            _send(
                email_type="request_received",
                recipient=lead.user,
                content=build_business_email_content(
                    "request_received",
                    name=_name(lead.user),
                    url=customer_url,
                ),
            )
            if lead.agent_id:
                agent_url = _url(reverse("agent-applicant-detail", kwargs={"lead_id": lead.pk}))
                for user in lead.agent.users.filter(is_active=True).exclude(pk=lead.user_id):
                    _send(
                        email_type="new_request_agent",
                        recipient=user,
                        content=build_business_email_content(
                            "new_request_agent",
                            applicant=str(lead),
                            url=agent_url,
                        ),
                    )

    _after_commit(deliver)


def notify_message(message) -> None:
    conversation = message.conversation
    if message.sender_role == "agent":
        recipients: Iterable = (conversation.customer,)
        email_type = "new_message_customer"
        target = conversation.get_customer_url()
    elif message.sender_role == "customer":
        recipients = conversation.agent.users.filter(is_active=True).exclude(pk=message.sender_id)
        email_type = "new_message_agent"
        target = conversation.get_agent_url()
    else:
        return

    def deliver():
        url = _url(target)
        for recipient in recipients:
            _send(
                email_type=email_type,
                recipient=recipient,
                content=build_business_email_content(email_type, url=url),
            )

    _after_commit(deliver)


def notify_program_recommended(*, lead, program) -> None:
    def deliver():
        _send(
            email_type="program_recommended",
            recipient=lead.user,
            content=build_business_email_content(
                "program_recommended",
                program=program.localized_name,
                university=program.university.localized_name,
                url=_url(reverse("lead-programs", kwargs={"lead_id": lead.pk})),
            ),
        )

    _after_commit(deliver)


def notify_document_action_required(*, lead, document) -> None:
    def deliver():
        _send(
            email_type="document_action_required",
            recipient=lead.user,
            content=build_business_email_content(
                "document_action_required",
                document=document.name or document.get_document_type_display(),
                reason=(document.review_note or "").strip(),
                url=_url(reverse("lead-documents", kwargs={"lead_id": lead.pk})),
            ),
        )

    _after_commit(deliver)


def notify_request_finalized(lead) -> None:
    def deliver():
        _send(
            email_type="request_moving_forward",
            recipient=lead.user,
            content=build_business_email_content(
                "request_moving_forward",
                url=_url(reverse("lead-detail", kwargs={"lead_id": lead.pk})),
            ),
        )

    _after_commit(deliver)


def notify_application_created(application) -> None:
    def deliver():
        offering = application.program_offering
        _send(
            email_type="application_started",
            recipient=application.student.user,
            content=build_business_email_content(
                "application_started",
                program=offering.program.localized_name,
                university=offering.program.university.localized_name,
                url=_url(
                    reverse(
                        "customer-application-detail",
                        kwargs={"application_id": application.pk},
                    )
                ),
            ),
        )

    _after_commit(deliver)


def notify_application_status_changed(*, application, old_status: str) -> None:
    if old_status == application.status:
        return

    def deliver():
        _send(
            email_type="application_status_updated",
            recipient=application.student.user,
            content=build_business_email_content(
                "application_status_updated",
                status=application.get_status_display(),
                url=_url(
                    reverse(
                        "customer-application-detail",
                        kwargs={"application_id": application.pk},
                    )
                ),
            ),
        )

    _after_commit(deliver)


def notify_todo_assigned(todo, *, performed_by=None) -> None:
    actor_id = getattr(performed_by, "pk", None) or todo.created_by_id
    if todo.assignee_id is None or todo.assignee_id == actor_id:
        return

    def deliver():
        _send(
            email_type="todo_assigned",
            recipient=todo.assignee,
            content=build_business_email_content(
                "todo_assigned",
                title=todo.title,
                due=todo.due_date,
                url=_url(reverse("agent-todo-list")),
            ),
        )

    _after_commit(deliver)
