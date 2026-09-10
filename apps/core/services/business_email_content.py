from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils.translation import gettext as _


@dataclass(frozen=True)
class BusinessEmailContent:
    subject: str
    lines: tuple[str, ...]

    @property
    def text_body(self) -> str:
        return "\n\n".join(line for line in self.lines if line)


def build_business_email_content(email_type: str, **context: Any) -> BusinessEmailContent:
    """Build production business-email copy from primitive, preview-safe context."""
    if email_type == "request_received":
        return BusinessEmailContent(
            subject=str(_("We received your TurkDemy request")),
            lines=(
                str(_("Hello %(name)s,") % {"name": context["name"]}),
                str(
                    _(
                        "We received your request. Your advisor will review it and "
                        "guide you through the next steps."
                    )
                ),
                str(_("View your request: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "new_request_agent":
        return BusinessEmailContent(
            subject=str(_("New TurkDemy request")),
            lines=(
                str(_("A new customer request is ready for review.")),
                str(_("Applicant: %(name)s") % {"name": context["applicant"]}),
                str(_("Open applicant: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type in {"new_message_customer", "new_message_agent"}:
        subject = (
            _("You have a new TurkDemy message")
            if email_type == "new_message_customer"
            else _("New message from a TurkDemy customer")
        )
        return BusinessEmailContent(
            subject=str(subject),
            lines=(
                str(_("There is a new message waiting for you in TurkDemy.")),
                str(_("Open the conversation: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "program_recommended":
        return BusinessEmailContent(
            subject=str(_("A new program was recommended for you")),
            lines=(
                str(
                    _("Your advisor recommended %(program)s at %(university)s.")
                    % {
                        "program": context["program"],
                        "university": context["university"],
                    }
                ),
                str(_("View your programs: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "document_action_required":
        reason = str(context.get("reason") or "").strip()
        return BusinessEmailContent(
            subject=str(_("A document needs your attention")),
            lines=(
                str(_("A document in your TurkDemy request needs to be replaced.")),
                str(_("Document: %(document)s") % {"document": context["document"]}),
                str(_("Reason: %(reason)s") % {"reason": reason}) if reason else "",
                str(_("Review your documents: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "request_moving_forward":
        return BusinessEmailContent(
            subject=str(_("Your TurkDemy request is moving forward")),
            lines=(
                str(
                    _(
                        "We completed the initial review of your request and it is "
                        "moving to the next stage."
                    )
                ),
                str(_("View your request: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "application_started":
        return BusinessEmailContent(
            subject=str(_("Your university application has started")),
            lines=(
                str(
                    _("An application has been started for %(program)s at %(university)s.")
                    % {
                        "program": context["program"],
                        "university": context["university"],
                    }
                ),
                str(_("View application: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "application_status_updated":
        return BusinessEmailContent(
            subject=str(_("Your university application was updated")),
            lines=(
                str(
                    _("Your application status is now: %(status)s") % {"status": context["status"]}
                ),
                str(_("View application: %(url)s") % {"url": context["url"]}),
            ),
        )

    if email_type == "todo_assigned":
        due = context.get("due")
        return BusinessEmailContent(
            subject=str(_("A TurkDemy task was assigned to you")),
            lines=(
                str(_("Task: %(title)s") % {"title": context["title"]}),
                str(_("Due: %(due)s") % {"due": due}) if due else "",
                str(_("Open tasks: %(url)s") % {"url": context["url"]}),
            ),
        )

    raise ValueError(f"Unsupported business email type: {email_type!r}")
