
from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import ActiveActionsMixin, AuditAdminMixin

from .models import Agent, AgentDocument


class AgentDocumentInline(admin.TabularInline):
    model = AgentDocument
    extra = 0
    fields = ("name", "description", "file", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Agent)
class AgentAdmin(AuditAdminMixin, ActiveActionsMixin, admin.ModelAdmin):
    list_display = (
        "company_name",
        "email",
        "cell",
        "landline",
        "parent",
        "user_count",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = (
        "company_name",
        "email",
        "cell",
        "landline",
        "users__username",
        "users__email",
    )
    autocomplete_fields = ("parent",)
    filter_horizontal = ("users",)
    inlines = (AgentDocumentInline,)

    fieldsets = (
        (
            "Company",
            {
                "fields": (
                    "company_name",
                    "logo",
                    "logo_preview",
                    "is_active",
                    "parent",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "website",
                    "cell",
                    "landline",
                )
            },
        ),
        (
            "Users",
            {
                "fields": ("users",),
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )
    readonly_fields = ("logo_preview",)

    @admin.display(description="Users")
    def user_count(self, obj):
        return obj.users.count()

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if not obj.logo:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:180px;" />',
            obj.logo.url,
        )


@admin.register(AgentDocument)
class AgentDocumentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("name", "agent", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description", "agent__company_name")
    autocomplete_fields = ("agent",)
