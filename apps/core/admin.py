from django.contrib import admin


class AuditAdminMixin:
    """
    Shared admin behavior for BaseModel descendants.

    - audit fields are read-only
    - created_by is set once on creation
    - updated_by is refreshed on every admin save
    """

    audit_readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    def get_readonly_fields(self, request, obj=None):
        return (
            *super().get_readonly_fields(request, obj),  # type: ignore[misc]
            *self.audit_readonly_fields,
        )

    def save_model(self, request, obj, form, change):
        if not change and not getattr(obj, "created_by_id", None):
            obj.created_by = request.user

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)  # type: ignore[misc]


class ActiveActionsMixin:
    @admin.action(description="Mark selected records active")
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected records inactive")
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_actions(self, request):
        actions = super().get_actions(request)  # type: ignore[misc]
        actions["mark_active"] = (
            ActiveActionsMixin.mark_active,
            "mark_active",
            "Mark selected records active",
        )
        actions["mark_inactive"] = (
            ActiveActionsMixin.mark_inactive,
            "mark_inactive",
            "Mark selected records inactive",
        )
        return actions
