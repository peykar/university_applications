from django.urls import path

from . import views

urlpatterns = [
    path(
        "3rdparty/",
        views.allauth_connections_redirect,
        name="socialaccount_connections_redirect",
    ),
    path(
        "settings/sign-in-methods/",
        views.sign_in_methods,
        name="sign-in-methods",
    ),
    path(
        "settings/sign-in-methods/email/add/",
        views.add_login_email,
        name="add-login-email",
    ),
    path(
        "settings/sign-in-methods/email/<int:email_id>/primary/",
        views.make_login_email_primary,
        name="make-login-email-primary",
    ),
    path(
        "settings/sign-in-methods/email/<int:email_id>/remove/",
        views.remove_login_email,
        name="remove-login-email",
    ),
    path(
        "settings/sign-in-methods/social/<str:provider>/disconnect/",
        views.disconnect_social_account,
        name="disconnect-social-account",
    ),
]
