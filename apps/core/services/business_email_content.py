from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils.translation import gettext as _

from .email_branding import localized_email_brand_name


@dataclass(frozen=True)
class BusinessEmailContent:
    subject: str
    lines: tuple[str, ...]
    cta_label: str
    cta_url: str

    @property
    def text_body(self) -> str:
        body = "\n\n".join(line for line in self.lines if line)
        return f"{body}\n\n{self.cta_label}:\n{self.cta_url}"


def build_business_email_content(email_type: str, **context: Any) -> BusinessEmailContent:
    """Build production business-email copy from primitive, preview-safe context."""
    brand = localized_email_brand_name()

    if email_type == "request_received":
        return BusinessEmailContent(
            subject=str(_("We received your %(brand)s request") % {"brand": brand}),
            lines=(
                str(_("Hello %(name)s,") % {"name": context["name"]}),
                str(
                    _(
                        "We received your request. Your advisor will review it and "
                        "guide you through the next steps."
                    )
                ),
            ),
            cta_label=str(_("View your request")),
            cta_url=context["url"],
        )

    if email_type == "new_request_agent":
        return BusinessEmailContent(
            subject=str(_("New %(brand)s request") % {"brand": brand}),
            lines=(
                str(_("A new customer request is ready for review.")),
                str(_("Applicant: %(name)s") % {"name": context["applicant"]}),
            ),
            cta_label=str(_("Open applicant")),
            cta_url=context["url"],
        )

    if email_type in {"new_message_customer", "new_message_agent"}:
        subject = (
            _("You have a new %(brand)s message") % {"brand": brand}
            if email_type == "new_message_customer"
            else _("New message from a %(brand)s customer") % {"brand": brand}
        )
        return BusinessEmailContent(
            subject=str(subject),
            lines=(
                str(_("There is a new message waiting for you in %(brand)s.") % {"brand": brand}),
            ),
            cta_label=str(_("Open the conversation")),
            cta_url=context["url"],
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
            ),
            cta_label=str(_("View your programs")),
            cta_url=context["url"],
        )

    if email_type == "document_action_required":
        reason = str(context.get("reason") or "").strip()
        return BusinessEmailContent(
            subject=str(_("A document needs your attention")),
            lines=(
                str(
                    _("A document in your %(brand)s request needs to be replaced.")
                    % {"brand": brand}
                ),
                str(_("Document: %(document)s") % {"document": context["document"]}),
                str(_("Reason: %(reason)s") % {"reason": reason}) if reason else "",
            ),
            cta_label=str(_("Review your documents")),
            cta_url=context["url"],
        )

    if email_type == "request_moving_forward":
        return BusinessEmailContent(
            subject=str(_("Your %(brand)s request is moving forward") % {"brand": brand}),
            lines=(
                str(
                    _(
                        "We completed the initial review of your request and it is "
                        "moving to the next stage."
                    )
                ),
            ),
            cta_label=str(_("View your request")),
            cta_url=context["url"],
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
            ),
            cta_label=str(_("View application")),
            cta_url=context["url"],
        )

    if email_type == "application_status_updated":
        return BusinessEmailContent(
            subject=str(_("Your university application was updated")),
            lines=(
                str(
                    _("Your application status is now: %(status)s") % {"status": context["status"]}
                ),
            ),
            cta_label=str(_("View application")),
            cta_url=context["url"],
        )

    if email_type == "todo_assigned":
        due = context.get("due")
        return BusinessEmailContent(
            subject=str(_("A %(brand)s task was assigned to you") % {"brand": brand}),
            lines=(
                str(_("Task: %(title)s") % {"title": context["title"]}),
                str(_("Due: %(due)s") % {"due": due}) if due else "",
            ),
            cta_label=str(_("Open tasks")),
            cta_url=context["url"],
        )

    raise ValueError(f"Unsupported business email type: {email_type!r}")
