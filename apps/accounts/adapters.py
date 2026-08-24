from __future__ import annotations

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth.models import AbstractBaseUser

from .models import User
from .social_email import ensure_verified_login_email


class TurkDemySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Preserve an existing local password when a trusted provider authenticates
    the same verified email address.

    django-allauth intentionally makes the local password unusable when social
    email authentication targets a local email that allauth does not yet know
    to be verified. That is a safe default for legacy/unverified accounts.

    For Google, the provider supplies a verified email address. Before allauth
    accepts that email-authenticated login, TurkDemy records the matching local
    email as verified. This keeps an existing password usable while still
    allowing Google to connect/login to the same canonical User.
    """

    TRUSTED_VERIFIED_EMAIL_PROVIDERS = frozenset({"google"})

    def authenticate_by_email(
        self,
        sociallogin: SocialLogin,
    ) -> tuple[AbstractBaseUser, str] | None:
        result = super().authenticate_by_email(sociallogin)
        if result is None:
            return None

        user, email = result

        if sociallogin.account.provider not in self.TRUSTED_VERIFIED_EMAIL_PROVIDERS:
            return result

        provider_verified_emails = {
            address.email.lower() for address in sociallogin.email_addresses if address.verified
        }
        if email.lower() not in provider_verified_emails:
            return result

        self._ensure_verified_email(user, email)
        return user, email

    @staticmethod
    def _ensure_verified_email(user: AbstractBaseUser, email: str) -> None:
        if isinstance(user, User):
            ensure_verified_login_email(user, email)
