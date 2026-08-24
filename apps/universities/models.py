from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import ActiveMixin, LocalizedNameMixin, LocalizedSlugMixin
from apps.core.models import BaseModel
from apps.geography.models import City


class UniversityType(models.TextChoices):
    PUBLIC = "public", _("Public")
    PRIVATE = "private", _("Private")


class University(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    logo = models.ImageField(upload_to="universities/logos/", blank=True)
    banner = models.ImageField(upload_to="universities/banners/", blank=True)
    website = models.URLField(blank=True)

    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="universities")
    university_type = models.CharField(max_length=20, choices=UniversityType.choices)

    is_yok_recognized = models.BooleanField(
        default=False,
        help_text=_("Whether the university is recognized by YÖK (the Council of Higher Education of Türkiye)."),
    )
    is_moe_approved = models.BooleanField(
        default=False,
        help_text=_("Whether the university is approved by the relevant Ministry of Education for the target student market."),
    )
    is_moh_approved = models.BooleanField(
        default=False,
        help_text=_("Whether the university is approved by the relevant Ministry of Health for the target student market."),
    )
    has_erasmus = models.BooleanField(
        default=False,
        help_text=_("Whether the university participates in the Erasmus+ mobility programme."),
    )
    has_dormitory = models.BooleanField(
        default=False,
        help_text=_("Whether the university provides or officially offers student dormitory accommodation."),
    )

    ranking_qs = models.PositiveIntegerField(null=True, blank=True, help_text=_("University ranking position according to QS World University Rankings."))
    ranking_the = models.PositiveIntegerField(null=True, blank=True, help_text=_("University ranking position according to Times Higher Education (THE)."))
    ranking_arwu = models.PositiveIntegerField(null=True, blank=True, help_text=_("University ranking position according to ARWU."))
    ranking_urap = models.PositiveIntegerField(null=True, blank=True, help_text=_("University ranking position according to URAP."))

    is_featured = models.BooleanField(default=False)
    listing_priority = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Internal priority used to influence this item's position in listings. Higher values receive greater priority."),
    )

    def __str__(self):
        return self.name_en


class UniversityMedia(BaseModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="media")
    image = models.ImageField(upload_to="universities/media/")
    title = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class Department(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="departments")
    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    def __str__(self):
        return self.name_en


class ProgramLanguage(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    def __str__(self):
        return self.name_en


class AcademicYear(BaseModel, ActiveMixin):
    name_en = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50, blank=True)
    name_tr = models.CharField(max_length=50, blank=True)
    name_ar = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name_en


class Semester(BaseModel, ActiveMixin):
    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100, blank=True)
    name_tr = models.CharField(max_length=100, blank=True)
    name_ar = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name_en


class DegreeType(models.TextChoices):
    ASSOCIATE = "associate", _("Associate")
    BACHELOR = "bachelor", _("Bachelor")
    MASTER = "master", _("Master")
    PHD = "phd", _("PhD")


class ThesisType(models.TextChoices):
    THESIS = "thesis", _("With Thesis")
    NON_THESIS = "non_thesis", _("Without Thesis")


class Program(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="programs")
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="programs",
        null=True,
        blank=True,
    )

    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    degree = models.CharField(max_length=20, choices=DegreeType.choices)
    thesis_type = models.CharField(
        max_length=20,
        choices=ThesisType.choices,
        null=True,
        blank=True,
        help_text=_("Indicates whether a graduate program is thesis or non-thesis, when applicable."),
    )
    program_language = models.ForeignKey(ProgramLanguage, on_delete=models.PROTECT, related_name="programs")
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    listing_priority = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_("Internal priority used to influence this item's position in listings. Higher values receive greater priority."),
    )

    def clean(self):
        super().clean()
        if self.department_id and self.department.university_id != self.university_id:
            from django.core.exceptions import ValidationError
            raise ValidationError({"department": _("Department must belong to the selected university.")})

    def __str__(self):
        return self.name_en


class Currency(models.TextChoices):
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    TRY = "TRY", _("Turkish Lira")


class FeeBasis(models.TextChoices):
    ANNUAL = "annual", _("Annual")
    WHOLE_PROGRAM = "whole_program", _("Total (Whole Program)")


class ProgramOffering(BaseModel, ActiveMixin):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="offerings")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="program_offerings")
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="program_offerings")

    fee_basis = models.CharField(
        max_length=30,
        choices=FeeBasis.choices,
        help_text=_("Specifies what period or unit the tuition amount applies to, such as per year or for the full program."),
    )
    currency = models.CharField(max_length=3, choices=Currency.choices)
    tuition = models.DecimalField(max_digits=12, decimal_places=2, help_text=_("Standard tuition amount before discounts for this program offering."))
    tuition_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tuition_discounted = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cash_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tuition_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tuition_annual_installment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pre_school_fees = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quota = models.PositiveIntegerField(null=True, blank=True, help_text=_("Number of admission places available for this offering, when known."))
    deadline = models.DateField(null=True, blank=True, help_text=_("Last date on which an application can be submitted for this offering."))

    def __str__(self):
        return f"{self.program} - {self.academic_year} - {self.semester}"
