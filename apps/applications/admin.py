from django.contrib import admin

from apps.core.admin import AuditAdminMixin

from .models import Application, ApplicationDocument


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    fields = (
        "student_document",
        "is_required",
        "is_verified",
        "verification_notes",
        "created_at",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ("student_document",)


@admin.register(Application)
class ApplicationAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "student",
        "university_name",
        "program_name",
        "academic_year",
        "semester",
        "agent",
        "status",
        "tuition",
        "deposit",
        "created_at",
    )
    list_filter = (
        "status",
        "program_offering__program__university",
        "program_offering__academic_year",
        "program_offering__semester",
        "agent",
        "created_at",
    )
    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__email",
        "student__passport_no",
        "program_offering__program__name_en",
        "program_offering__program__university__name_en",
        "agent__company_name",
    )
    autocomplete_fields = (
        "student",
        "agent",
        "program_offering",
    )
    inlines = (ApplicationDocumentInline,)

    @admin.display(description="University")
    def university_name(self, obj):
        return obj.program_offering.program.university.name_en

    @admin.display(description="Program")
    def program_name(self, obj):
        return obj.program_offering.program.name_en

    @admin.display(description="Academic year")
    def academic_year(self, obj):
        return obj.program_offering.academic_year.name_en

    @admin.display(description="Semester")
    def semester(self, obj):
        return obj.program_offering.semester.name_en

    @admin.action(description="Mark selected applications under review")
    def mark_under_review(self, request, queryset):
        queryset.update(status="under_review")

    @admin.action(description="Mark selected applications accepted")
    def mark_accepted(self, request, queryset):
        queryset.update(status="accepted")

    @admin.action(description="Mark selected applications rejected")
    def mark_rejected(self, request, queryset):
        queryset.update(status="rejected")

    actions = (
        "mark_under_review",
        "mark_accepted",
        "mark_rejected",
    )


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "application",
        "student_document",
        "is_required",
        "is_verified",
        "created_at",
    )
    list_filter = (
        "is_required",
        "is_verified",
        "created_at",
    )
    search_fields = (
        "application__student__first_name",
        "application__student__last_name",
        "student_document__short_description",
    )
    autocomplete_fields = (
        "application",
        "student_document",
    )

    @admin.action(description="Mark selected documents verified")
    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description="Mark selected documents unverified")
    def mark_unverified(self, request, queryset):
        queryset.update(is_verified=False)

    actions = (
        "mark_verified",
        "mark_unverified",
    )
