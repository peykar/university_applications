from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import AuditAdminMixin

from .models import CommunicationLog, CommunicationLogRevision, Todo, TodoComment


class TodoCommentInline(admin.TabularInline):
    model = TodoComment
    extra = 0
    fields = ("author", "body", "created_at")
    readonly_fields = ("author", "body", "created_at")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class CommunicationLogRevisionInline(admin.TabularInline):
    model = CommunicationLogRevision
    extra = 0
    fields = ("revised_by", "created_at", "snapshot")
    readonly_fields = ("revised_by", "created_at", "snapshot")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Todo)
class TodoAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "agent",
        "status",
        "assignee",
        "due_date",
        "due_state",
        "subject_label",
        "updated_at",
    )
    list_filter = ("status", "agent", "due_date", "assignee", "created_at", "updated_at")
    search_fields = (
        "title",
        "description",
        "agent__company_name",
        "assignee__username",
        "assignee__email",
        "assignee__first_name",
        "assignee__last_name",
    )
    autocomplete_fields = ("agent", "assignee", "completed_by")
    readonly_fields = ("completed_by", "completed_at", "subject_label")
    date_hierarchy = "due_date"
    ordering = ("status", "due_date", "-created_at")
    list_select_related = ("agent", "assignee", "completed_by", "subject_content_type")
    list_per_page = 50
    inlines = (TodoCommentInline,)
    fieldsets = (
        (
            "TODO",
            {"fields": ("agent", "title", "description", "status", "assignee", "due_date")},
        ),
        (
            "Subject",
            {
                "fields": ("subject_label", "subject_content_type", "subject_object_id"),
                "description": "Optional generic object this TODO belongs to.",
            },
        ),
        (
            "Completion",
            {"fields": ("completed_by", "completed_at")},
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )

    @admin.display(description="Subject")
    def subject_label(self, obj):
        if not obj.pk or obj.subject is None:
            return "—"
        return str(obj.subject)

    @admin.display(description="Due", ordering="due_date")
    def due_state(self, obj):
        if obj.due_date is None:
            return "—"
        if obj.status in {"done", "cancelled"}:
            return "Closed"
        from django.utils import timezone

        today = timezone.localdate()
        if obj.due_date < today:
            return format_html('<strong style="color:#ba2121">Overdue</strong>')
        if obj.due_date == today:
            return format_html('<strong style="color:#b36b00">Today</strong>')
        return "Upcoming"


@admin.register(TodoComment)
class TodoCommentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("todo", "author", "body_preview", "created_at")
    list_filter = ("todo__agent", "created_at")
    search_fields = (
        "body",
        "todo__title",
        "todo__agent__company_name",
        "author__username",
        "author__email",
    )
    autocomplete_fields = ("todo", "author")
    readonly_fields = (
        "todo",
        "author",
        "body",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_select_related = ("todo", "todo__agent", "author")
    date_hierarchy = "created_at"
    list_per_page = 50

    @admin.display(description="Comment")
    def body_preview(self, obj):
        return obj.body if len(obj.body) <= 100 else f"{obj.body[:97]}..."

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CommunicationLog)
class CommunicationLogAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "occurred_at",
        "agent",
        "channel",
        "counterparty_type",
        "counterparty_name",
        "performed_by",
        "subject_label",
        "summary_preview",
    )
    list_filter = (
        "channel",
        "counterparty_type",
        "agent",
        "performed_by",
        "occurred_at",
        "created_at",
    )
    search_fields = (
        "summary",
        "counterparty_name",
        "agent__company_name",
        "performed_by__username",
        "performed_by__email",
        "performed_by__first_name",
        "performed_by__last_name",
    )
    autocomplete_fields = ("agent", "performed_by")
    readonly_fields = ("subject_label",)
    date_hierarchy = "occurred_at"
    ordering = ("-occurred_at", "-created_at")
    list_select_related = ("agent", "performed_by", "subject_content_type")
    list_per_page = 50
    inlines = (CommunicationLogRevisionInline,)
    fieldsets = (
        (
            "Communication",
            {
                "fields": (
                    "agent",
                    "performed_by",
                    "occurred_at",
                    "channel",
                    "counterparty_type",
                    "counterparty_name",
                    "summary",
                )
            },
        ),
        (
            "Subject",
            {
                "fields": ("subject_label", "subject_content_type", "subject_object_id"),
                "description": "Optional generic object this communication concerns.",
            },
        ),
        (
            "Audit",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )

    @admin.display(description="Subject")
    def subject_label(self, obj):
        if not obj.pk or obj.subject is None:
            return "—"
        return str(obj.subject)

    @admin.display(description="Summary")
    def summary_preview(self, obj):
        return obj.summary if len(obj.summary) <= 100 else f"{obj.summary[:97]}..."


@admin.register(CommunicationLogRevision)
class CommunicationLogRevisionAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("communication", "revised_by", "created_at")
    list_filter = ("communication__agent", "revised_by", "created_at")
    search_fields = (
        "communication__summary",
        "communication__counterparty_name",
        "communication__agent__company_name",
        "revised_by__username",
        "revised_by__email",
    )
    autocomplete_fields = ("communication", "revised_by")
    readonly_fields = (
        "communication",
        "revised_by",
        "snapshot",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_select_related = ("communication", "communication__agent", "revised_by")
    date_hierarchy = "created_at"
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
