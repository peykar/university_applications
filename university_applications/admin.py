from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    AcademicYear,
    Agent,
    AgentDocument,
    Application,
    ApplicationDocument,
    City,
    ContactSubmission,
    Country,
    Department,
    FAQ,
    FAQCategory,
    Program,
    ProgramLanguage,
    ProgramOffering,
    Province,
    Semester,
    Student,
    StudentDocument,
    University,
    UniversityMedia,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("username",)
    list_display = ("username", "email", "cell", "is_staff", "is_active")
    search_fields = ("username", "email", "cell", "telegram", "telegram_id")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "cell", "telegram", "telegram_id")},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


class UniversityMediaInline(admin.TabularInline):
    model = UniversityMedia
    extra = 0


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "city",
        "university_type",
        "listing_priority",
        "is_active",
        "is_featured",
    )
    list_filter = ("university_type", "is_active", "is_featured", "has_erasmus", "has_dormitory")
    search_fields = ("name_en", "name_fa", "name_tr", "name_ar", "city__name_en")
    inlines = [UniversityMediaInline]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name_en", "university", "degree", "program_language", "listing_priority", "is_active")
    list_filter = ("degree", "program_language", "is_active")
    search_fields = ("name_en", "name_fa", "name_tr", "university__name_en", "department__name_en")


@admin.register(ProgramOffering)
class ProgramOfferingAdmin(admin.ModelAdmin):
    list_display = ("program", "academic_year", "semester", "currency", "tuition", "deadline", "is_active")
    list_filter = ("academic_year", "semester", "currency", "fee_basis", "is_active")
    search_fields = ("program__name_en", "program__university__name_en")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "nationality", "email", "cell", "agent")
    search_fields = ("first_name", "middle_name", "last_name", "email", "cell", "passport_no")
    list_filter = ("nationality", "gender")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "program_offering", "status", "tuition", "created_at")
    list_filter = ("status", "program_offering__academic_year", "program_offering__semester")
    search_fields = ("student__first_name", "student__last_name", "program_offering__program__name_en")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "cell", "landline", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("company_name", "email", "cell", "landline", "users__username", "users__email")
    filter_horizontal = ("users",)


@admin.register(AgentDocument)
class AgentDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "agent", "created_at", "updated_at")
    search_fields = ("name", "description", "agent__company_name")
    list_filter = ("created_at",)


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("key", "display_name", "sort_order", "faq_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("key", "name_en", "name_fa", "name_tr", "name_ar")

    @admin.display(description="Name")
    def display_name(self, obj):
        return obj.localized_name("en") or obj.localized_name("fa") or obj.key


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("display_question", "category", "topic", "view_count", "is_active")
    list_filter = ("category", "topic", "is_active")
    search_fields = ("question_en", "question_fa", "question_tr", "question_ar", "answer_en", "answer_fa")
    autocomplete_fields = ("category",)

    @admin.display(description="Question")
    def display_question(self, obj):
        return obj.localized_question("en") or obj.localized_question("fa")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "handled", "created_at")
    list_filter = ("handled", "created_at")
    search_fields = ("name", "email", "phone_number", "subject", "message")
    readonly_fields = ("created_at", "updated_at")


for model in [
    Country,
    Province,
    City,
    Department,
    ProgramLanguage,
    AcademicYear,
    Semester,
    StudentDocument,
    ApplicationDocument,
]:
    admin.site.register(model)
