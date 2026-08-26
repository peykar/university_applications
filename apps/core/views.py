from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .email_previews import EMAIL_PREVIEW_REGISTRY, render_email_preview


def page_not_found(request, exception=None):
    response = render(
        request,
        "errors/404.html",
        status=404,
    )
    response["X-TurkDemy-Error-Page"] = "1"
    return response


def _require_superuser(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404


def email_preview_gallery(request):
    _require_superuser(request)

    languages = list(settings.LANGUAGES)
    categories: dict[str, list] = {}
    for spec in EMAIL_PREVIEW_REGISTRY.values():
        categories.setdefault(spec.category, []).append(spec)

    return render(
        request,
        "admin_tools/email_preview_gallery.html",
        {
            "categories": categories,
            "languages": languages,
            "email_count": len(EMAIL_PREVIEW_REGISTRY),
            "preview_count": len(EMAIL_PREVIEW_REGISTRY) * len(languages),
        },
    )


def email_preview_detail(request, email_type, language):
    _require_superuser(request)

    supported_languages = dict(settings.LANGUAGES)
    if email_type not in EMAIL_PREVIEW_REGISTRY or language not in supported_languages:
        raise Http404

    preview = render_email_preview(
        email_type=email_type,
        language=language,
    )
    english = (
        preview if language == "en" else render_email_preview(email_type=email_type, language="en")
    )
    preview["possibly_untranslated"] = (
        language != "en"
        and preview["subject"] == english["subject"]
        and preview["text_body"] == english["text_body"]
    )

    return render(
        request,
        "admin_tools/email_preview_detail.html",
        {
            **preview,
            "language_name": supported_languages[language],
        },
    )


@require_POST
def send_email_preview(request, email_type, language):
    _require_superuser(request)

    if email_type not in EMAIL_PREVIEW_REGISTRY or language not in dict(settings.LANGUAGES):
        raise Http404

    recipient = request.user.email
    if not recipient:
        messages.error(
            request,
            "Your superuser account has no email address.",
        )
        return redirect(
            "email-preview-detail",
            email_type=email_type,
            language=language,
        )

    preview = render_email_preview(
        email_type=email_type,
        language=language,
    )
    preview["message"].to = [recipient]
    preview["message"].send()

    messages.success(
        request,
        f"Test email sent to {recipient}.",
    )
    return redirect(
        reverse(
            "email-preview-detail",
            kwargs={"email_type": email_type, "language": language},
        )
    )
