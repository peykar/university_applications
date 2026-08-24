from django.contrib import admin

from apps.core.admin import AuditAdminMixin

from .models import Student, StudentDocument


class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0
    fields = (
        "document_type",
        "file",
        "short_description",
        "created_at",
    )
    readonly_fields = ("created_at",)


@admin.register(Student)
class StudentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = (
        "full_name",
        "nationality",
        "country_of_residence",
        "city_of_residence",
        "agent",
        "email",
        "cell",
        "created_at",
    )
    list_filter = (
        "nationality",
        "country_of_residence",
        "gender",
        "agent",
        "created_at",
    )
    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "cell",
        "passport_no",
        "user__username",
        "user__email",
    )
    autocomplete_fields = (
        "user",
        "agent",
        "country_of_birth",
        "nationality",
        "country_of_residence",
    )
    inlines = (StudentDocumentInline,)

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "user",
                    "agent",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "gender",
                    "birthdate",
                    "country_of_birth",
                    "nationality",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "cell",
                    "country_of_residence",
                    "city_of_residence",
                    "address",
                )
            },
        ),
        (
            "Education",
            {
                "fields": (
                    "english_test_type",
                    "english_language_test_score",
                    "high_school_gpa",
                    "high_school_gpa_scale",
                    "educational_background",
                )
            },
        ),
        (
            "Family",
            {
                "classes": ("collapse",),
                "fields": (
                    "father_name",
                    "mother_name",
                ),
            },
        ),
        (
            "Passport",
            {
                "fields": (
                    "passport_no",
                    "passport_issuing_authority",
                    "passport",
                    "passport_date_of_issue",
                    "passport_date_of_expiry",
                )
            },
        ),
        (
            "Internal",
            {
                "fields": (
                    "notes",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                )
            },
        ),
    )

    @admin.display(description="Student", ordering="last_name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


@admin.register(StudentDocument)
class StudentDocumentAdmin(AuditAdminMixin, admin.ModelAdmin):
    list_display = ("student", "document_type", "short_description", "created_at")
    list_filter = ("document_type", "created_at")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "short_description",
    )
    autocomplete_fields = ("student",)
