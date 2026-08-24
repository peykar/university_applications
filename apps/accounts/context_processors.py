from django.conf import settings
from django.http import HttpRequest


def authentication_providers(request: HttpRequest) -> dict[str, bool]:
    return {
        "google_login_enabled": settings.GOOGLE_LOGIN_ENABLED,
        "telegram_login_enabled": settings.TELEGRAM_LOGIN_ENABLED,
    }
