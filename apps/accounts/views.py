from __future__ import annotations

from typing import cast

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import AddLoginEmailForm
from .models import User


def _usable_login_method_count(user) -> int:
    social_count = SocialAccount.objects.filter(user=user).count()
    verified_email_count = EmailAddress.objects.filter(
        user=user,
        verified=True,
    ).count()
    password_count = 1 if user.has_usable_password() else 0
    return social_count + verified_email_count + password_count


@login_required
def sign_in_methods(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    social_accounts = {
        account.provider: account for account in SocialAccount.objects.filter(user=user)
    }
    email_addresses = EmailAddress.objects.filter(user=user).order_by(
        "-primary",
        "-verified",
        "email",
    )

    return render(
        request,
        "accounts/sign_in_methods.html",
        {
            "google_account": social_accounts.get("google"),
            "telegram_account": social_accounts.get("telegram"),
            "email_addresses": email_addresses,
            "has_verified_email": email_addresses.filter(verified=True).exists(),
            "add_email_form": AddLoginEmailForm(user=user),
            "usable_login_method_count": _usable_login_method_count(user),
        },
    )


@login_required
@require_POST
@transaction.atomic
def add_login_email(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = AddLoginEmailForm(request.POST, user=user)

    if not form.is_valid():
        social_accounts = {
            account.provider: account for account in SocialAccount.objects.filter(user=user)
        }
        return render(
            request,
            "accounts/sign_in_methods.html",
            {
                "google_account": social_accounts.get("google"),
                "telegram_account": social_accounts.get("telegram"),
                "email_addresses": EmailAddress.objects.filter(user=user).order_by(
                    "-primary", "-verified", "email"
                ),
                "has_verified_email": EmailAddress.objects.filter(
                    user=user,
                    verified=True,
                ).exists(),
                "add_email_form": form,
                "usable_login_method_count": _usable_login_method_count(user),
            },
            status=400,
        )

    email = form.cleaned_data["email"]

    address, address_created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
        defaults={
            "verified": False,
            "primary": not EmailAddress.objects.filter(user=user).exists(),
        },
    )

    del address_created

    if address.verified:
        messages.info(request, _("That email address is already verified."))
        return redirect("sign-in-methods")

    address.send_confirmation(request=request)
    messages.success(
        request,
        _("We sent a verification email to %(email)s.") % {"email": email},
    )
    return redirect("sign-in-methods")


@login_required
@require_POST
@transaction.atomic
def make_login_email_primary(request: HttpRequest, email_id: int) -> HttpResponse:
    user = cast(User, request.user)
    address = EmailAddress.objects.filter(
        pk=email_id,
        user=user,
    ).first()
    if address is None:
        raise Http404

    if not address.verified:
        messages.error(request, _("Verify this email address before making it primary."))
        return redirect("sign-in-methods")

    EmailAddress.objects.filter(user=user, primary=True).exclude(pk=address.pk).update(
        primary=False
    )

    if not address.primary:
        address.primary = True
        address.save(update_fields=["primary"])

    user.email = address.email
    user.save(update_fields=["email"])

    messages.success(request, _("Primary email updated."))
    return redirect("sign-in-methods")


@login_required
@require_POST
@transaction.atomic
def remove_login_email(request: HttpRequest, email_id: int) -> HttpResponse:
    user = cast(User, request.user)
    address = EmailAddress.objects.filter(
        pk=email_id,
        user=user,
    ).first()
    if address is None:
        raise Http404

    if address.verified and _usable_login_method_count(user) <= 1:
        messages.error(
            request,
            _("Add another sign-in method before removing your last login method."),
        )
        return redirect("sign-in-methods")

    was_primary = address.primary
    removed_email = address.email
    address.delete()

    if was_primary:
        replacement = (
            EmailAddress.objects.filter(
                user=user,
                verified=True,
            )
            .order_by("-verified", "email")
            .first()
        )

        if replacement is not None:
            replacement.primary = True
            replacement.save(update_fields=["primary"])
            user.email = replacement.email
        elif user.email and user.email.lower() == removed_email.lower():
            user.email = None

        user.save(update_fields=["email"])

    messages.success(request, _("Email sign-in method removed."))
    return redirect("sign-in-methods")


@login_required
@require_POST
@transaction.atomic
def disconnect_social_account(
    request: HttpRequest,
    provider: str,
) -> HttpResponse:
    user = cast(User, request.user)

    if provider not in {"google", "telegram"}:
        raise Http404

    account = SocialAccount.objects.filter(
        user=user,
        provider=provider,
    ).first()
    if account is None:
        raise Http404

    if _usable_login_method_count(user) <= 1:
        messages.error(
            request,
            _("Add another sign-in method before disconnecting your last login method."),
        )
        return redirect("sign-in-methods")

    account.delete()

    if provider == "telegram":
        changed_fields = []
        if user.telegram_id:
            user.telegram_id = None
            changed_fields.append("telegram_id")
        if user.telegram:
            user.telegram = None
            changed_fields.append("telegram")
        if changed_fields:
            user.save(update_fields=changed_fields)

    messages.success(
        request,
        _("%(provider)s disconnected.") % {"provider": provider.title()},
    )
    return redirect("sign-in-methods")


@login_required
def allauth_connections_redirect(request: HttpRequest) -> HttpResponse:
    """Redirect django-allauth's default connection UI to TurkDemy's UI."""
    return redirect("sign-in-methods")
