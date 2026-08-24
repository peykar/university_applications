from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "cell",
        "is_cell_verified",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    search_fields = (
        "username",
        "email",
        "cell",
        "telegram",
        "telegram_id",
        "first_name",
        "last_name",
    )
    readonly_fields = ("cell_verified_at", "date_joined")

    fieldsets = (
        *(UserAdmin.fieldsets or ()),
        (
            "Additional identities",
            {
                "fields": (
                    "cell",
                    "cell_verified_at",
                    "telegram",
                    "telegram_id",
                )
            },
        ),
    )

    add_fieldsets = (
        *(UserAdmin.add_fieldsets or ()),
        (
            "Additional identities",
            {
                "fields": (
                    "email",
                    "cell",
                    "telegram",
                    "telegram_id",
                )
            },
        ),
    )
