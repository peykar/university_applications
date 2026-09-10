from __future__ import annotations

import logging
from collections.abc import Iterable

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

from .emailing import send_email

logger = logging.getLogger(__name__)


def _url(path: str) -> str:
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def _name(user) -> str:
    return (user.get_full_name() or user.get_username() or user.email).strip()


def _send(*, email_type: str, recipient, subject: str, lines: list[str]) -> None:
    email = getattr(recipient, "email", "")
    if not email:
        return
    text = "\n\n".join(line for line in lines if line)
    send_email(email_type=email_type, subject=subject, to=email, text_body=text)


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
                subject=str(_("We received your TurkDemy request")),
                lines=[
                    str(_("Hello %(name)s,") % {"name": _name(lead.user)}),
                    str(
                        _(
                            "We received your request. Your advisor will review it and "
                            "guide you through the next steps."
                        )
                    ),
                    str(_("View your request: %(url)s") % {"url": customer_url}),
                ],
            )
            if lead.agent_id:
                agent_url = _url(reverse("agent-applicant-detail", kwargs={"lead_id": lead.pk}))
                for user in lead.agent.users.filter(is_active=True).exclude(pk=lead.user_id):
                    _send(
                        email_type="new_request_agent",
                        recipient=user,
                        subject=str(_("New TurkDemy request")),
                        lines=[
                            str(_("A new customer request is ready for review.")),
                            str(_("Applicant: %(name)s") % {"name": str(lead)}),
                            str(_("Open applicant: %(url)s") % {"url": agent_url}),
                        ],
                    )

    _after_commit(deliver)


def notify_message(message) -> None:
    conversation = message.conversation
    if message.sender_role == "agent":
        recipients: Iterable = (conversation.customer,)
        email_type = "new_message_customer"
        target = conversation.get_customer_url()
        subject = _("You have a new TurkDemy message")
    elif message.sender_role == "customer":
        recipients = conversation.agent.users.filter(is_active=True).exclude(pk=message.sender_id)
        email_type = "new_message_agent"
        target = conversation.get_agent_url()
        subject = _("New message from a TurkDemy customer")
    else:
        return

    def deliver():
        url = _url(target)
        for recipient in recipients:
            _send(
                email_type=email_type,
                recipient=recipient,
                subject=str(subject),
                lines=[
                    str(_("There is a new message waiting for you in TurkDemy.")),
                    str(_("Open the conversation: %(url)s") % {"url": url}),
                ],
            )

    _after_commit(deliver)


def notify_program_recommended(*, lead, program) -> None:
    def deliver():
        _send(
            email_type="program_recommended",
            recipient=lead.user,
            subject=str(_("A new program was recommended for you")),
            lines=[
                str(
                    _("Your advisor recommended %(program)s at %(university)s.")
                    % {
                        "program": program.localized_name,
                        "university": program.university.localized_name,
                    }
                ),
                str(
                    _("View your programs: %(url)s")
                    % {"url": _url(reverse("lead-programs", kwargs={"lead_id": lead.pk}))}
                ),
            ],
        )

    _after_commit(deliver)


def notify_document_action_required(*, lead, document) -> None:
    def deliver():
        reason = (document.review_note or "").strip()
        _send(
            email_type="document_action_required",
            recipient=lead.user,
            subject=str(_("A document needs your attention")),
            lines=[
                str(_("A document in your TurkDemy request needs to be replaced.")),
                str(
                    _("Document: %(document)s")
                    % {"document": document.name or document.get_document_type_display()}
                ),
                str(_("Reason: %(reason)s") % {"reason": reason}) if reason else "",
                str(
                    _("Review your documents: %(url)s")
                    % {"url": _url(reverse("lead-documents", kwargs={"lead_id": lead.pk}))}
                ),
            ],
        )

    _after_commit(deliver)


def notify_request_finalized(lead) -> None:
    def deliver():
        _send(
            email_type="request_moving_forward",
            recipient=lead.user,
            subject=str(_("Your TurkDemy request is moving forward")),
            lines=[
                str(
                    _(
                        "We completed the initial review of your request and it is "
                        "moving to the next stage."
                    )
                ),
                str(
                    _("View your request: %(url)s")
                    % {"url": _url(reverse("lead-detail", kwargs={"lead_id": lead.pk}))}
                ),
            ],
        )

    _after_commit(deliver)


def notify_application_created(application) -> None:
    def deliver():
        offering = application.program_offering
        _send(
            email_type="application_started",
            recipient=application.student.user,
            subject=str(_("Your university application has started")),
            lines=[
                str(
                    _("An application has been started for %(program)s at %(university)s.")
                    % {
                        "program": offering.program.localized_name,
                        "university": offering.program.university.localized_name,
                    }
                ),
                str(
                    _("View application: %(url)s")
                    % {
                        "url": _url(
                            reverse(
                                "customer-application-detail",
                                kwargs={"application_id": application.pk},
                            )
                        )
                    }
                ),
            ],
        )

    _after_commit(deliver)


def notify_application_status_changed(*, application, old_status: str) -> None:
    if old_status == application.status:
        return

    def deliver():
        _send(
            email_type="application_status_updated",
            recipient=application.student.user,
            subject=str(_("Your university application was updated")),
            lines=[
                str(
                    _("Your application status is now: %(status)s")
                    % {"status": application.get_status_display()}
                ),
                str(
                    _("View application: %(url)s")
                    % {
                        "url": _url(
                            reverse(
                                "customer-application-detail",
                                kwargs={"application_id": application.pk},
                            )
                        )
                    }
                ),
            ],
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
            subject=str(_("A TurkDemy task was assigned to you")),
            lines=[
                str(_("Task: %(title)s") % {"title": todo.title}),
                str(_("Due: %(due)s") % {"due": todo.due_date}) if todo.due_date else "",
                str(_("Open tasks: %(url)s") % {"url": _url(reverse("agent-todo-list"))}),
            ],
        )

    _after_commit(deliver)
