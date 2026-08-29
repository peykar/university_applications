from decimal import Decimal
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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
        help_text=_(
            "Whether the university is recognized by YÖK "
            "(the Council of Higher Education of Türkiye)."
        ),
    )
    is_moe_approved = models.BooleanField(
        default=False,
        help_text=_(
            "Whether the university is approved by the relevant Ministry of Education "
            "for the target student market."
        ),
    )
    is_moh_approved = models.BooleanField(
        default=False,
        help_text=_(
            "Whether the university is approved by the relevant Ministry of Health "
            "for the target student market."
        ),
    )
    has_erasmus = models.BooleanField(
        default=False,
        help_text=_("Whether the university participates in the Erasmus+ mobility programme."),
    )
    has_dormitory = models.BooleanField(
        default=False,
        help_text=_(
            "Whether the university provides or officially offers student dormitory accommodation."
        ),
    )

    ranking_qs = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("University ranking position according to QS World University Rankings."),
    )
    ranking_the = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("University ranking position according to Times Higher Education (THE)."),
    )
    ranking_arwu = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("University ranking position according to ARWU."),
    )
    ranking_urap = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("University ranking position according to URAP."),
    )

    is_featured = models.BooleanField(default=False)
    listing_priority = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_(
            "Internal priority used to influence this item's position in listings. "
            "Higher values receive greater priority."
        ),
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


class AcademicUnitType(models.TextChoices):
    FACULTY = "faculty", _("Faculty")
    SCHOOL = "school", _("School")
    INSTITUTE = "institute", _("Institute")
    VOCATIONAL_SCHOOL = "vocational_school", _("Vocational School")
    CONSERVATORY = "conservatory", _("Conservatory")
    COLLEGE = "college", _("College")
    GRADUATE_SCHOOL = "graduate_school", _("Graduate School")
    OTHER = "other", _("Other")


class AcademicUnit(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="academic_units"
    )
    unit_type = models.CharField(max_length=30, choices=AcademicUnitType.choices)
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


class StudyMode(models.TextChoices):
    ON_CAMPUS = "on_campus", _("On campus")
    DISTANCE = "distance", _("Distance learning")
    ONLINE = "online", _("Online")
    HYBRID = "hybrid", _("Hybrid")


class Program(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="programs")
    academic_unit = models.ForeignKey(
        AcademicUnit,
        on_delete=models.PROTECT,
        related_name="programs",
        null=True,
        blank=True,
    )
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
        help_text=_(
            "Indicates whether a graduate program is thesis or non-thesis, when applicable."
        ),
    )
    # Compatibility bridge for existing imported data. Canonical readers use
    # instruction_languages through ProgramInstructionLanguage.
    program_language = models.ForeignKey(
        ProgramLanguage,
        on_delete=models.PROTECT,
        related_name="legacy_programs",
        null=True,
        blank=True,
        help_text=_("Deprecated single-language compatibility field."),
    )
    instruction_languages: "models.ManyToManyField[ProgramLanguage, ProgramLanguage]" = (
        models.ManyToManyField(
            ProgramLanguage,
            through="ProgramInstructionLanguage",
            related_name="programs",
            blank=True,
        )
    )
    study_mode = models.CharField(
        max_length=20, choices=StudyMode.choices, default=StudyMode.ON_CAMPUS
    )
    # Compatibility bridge. Existing values represent years. New code stores
    # duration canonically in months so fractional years are lossless.
    duration = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text=_("Deprecated duration in whole years.")
    )
    duration_months = models.PositiveSmallIntegerField(null=True, blank=True)
    listing_priority = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_(
            "Internal priority used to influence this item's position in listings. "
            "Higher values receive greater priority."
        ),
    )

    def clean(self):
        super().clean()
        errors = {}
        department = self.department if self.department_id else None
        if department is not None and department.university_id != self.university_id:
            errors["department"] = _("Department must belong to the selected university.")
        academic_unit = self.academic_unit if self.academic_unit_id else None
        if academic_unit is not None and academic_unit.university_id != self.university_id:
            errors["academic_unit"] = _("Academic unit must belong to the selected university.")
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.duration_months is None and self.duration is not None:
            self.duration_months = self.duration * 12
        if self.duration is None and self.duration_months and self.duration_months % 12 == 0:
            self.duration = self.duration_months // 12
        super().save(*args, **kwargs)
        if self.program_language_id and not self.instruction_language_rows.exists():
            ProgramInstructionLanguage.objects.get_or_create(
                program=self,
                language_id=self.program_language_id,
                defaults={"is_primary": True},
            )

    @property
    def duration_display(self) -> str:
        if not self.duration_months:
            return ""
        months = self.duration_months
        if months % 12 == 0:
            years = months // 12
            if years == 1:
                return _("%(years)s year") % {"years": years}
            return _("%(years)s years") % {"years": years}
        if months % 6 == 0:
            fractional_years = Decimal(months) / Decimal(12)
            value = format(fractional_years.normalize(), "f")
            return _("%(years)s years") % {"years": value}
        return _("%(months)s months") % {"months": months}

    @property
    def instruction_language_display(self) -> str:
        rows = list(
            self.instruction_language_rows.select_related("language").order_by(
                "-is_primary", "language__name_en"
            )
        )
        if not rows and self.program_language_id:
            legacy_language = self.program_language
            if legacy_language is not None:
                return legacy_language.name_en
        parts = []
        for row in rows:
            if row.percentage is None:
                parts.append(row.language.name_en)
            else:
                percentage = format(row.percentage.normalize(), "f")
                parts.append(f"{percentage}% {row.language.name_en}")
        return " · ".join(parts)

    def __str__(self):
        return self.name_en


class ProgramInstructionLanguage(BaseModel):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="instruction_language_rows"
    )
    language = models.ForeignKey(
        ProgramLanguage, on_delete=models.PROTECT, related_name="program_language_rows"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("program", "language"),
                name="uniq_program_instruction_language",
            )
        ]

    def clean(self):
        super().clean()
        if self.percentage is None or not self.program_id:
            return
        other_percentages = self.program.instruction_language_rows.exclude(pk=self.pk).values_list(
            "percentage", flat=True
        )
        known = [value for value in other_percentages if value is not None]
        total = sum(known, Decimal("0")) + self.percentage
        if total > Decimal("100"):
            raise ValidationError(
                {"percentage": _("Instruction-language percentages cannot exceed 100%.")}
            )

    def __str__(self):
        return f"{self.program} — {self.language}"


class Currency(models.TextChoices):
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    TRY = "TRY", _("Turkish Lira")


class FeeBasis(models.TextChoices):
    ANNUAL = "annual", _("Annual")
    WHOLE_PROGRAM = "whole_program", _("Total (Whole Program)")


class UniversityCatalogueSource(BaseModel):
    university = models.ForeignKey(
        University, on_delete=models.PROTECT, related_name="catalogue_sources"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="universities/catalogue-sources/", blank=True)
    received_at = models.DateField()
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="catalogue_sources",
        null=True,
        blank=True,
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        related_name="recorded_catalogue_sources",
        null=True,
        blank=True,
    )

    def clean(self):
        super().clean()
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValidationError(
                {"valid_until": _("Valid until cannot be earlier than valid from.")}
            )

    def __str__(self):
        return f"{self.university} — {self.title}"


class ProgramOffering(BaseModel, ActiveMixin):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="offerings")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="program_offerings",
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="program_offerings",
    )

    fee_basis = models.CharField(
        max_length=30,
        choices=FeeBasis.choices,
        help_text=_(
            "Specifies what period or unit the tuition amount applies to, "
            "such as per year or for the full program."
        ),
    )
    currency = models.CharField(max_length=3, choices=Currency.choices)
    tuition = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Standard tuition amount before discounts for this program offering."),
    )
    tuition_discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    tuition_discounted = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cash_discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    tuition_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tuition_annual_installment = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preparatory_tuition = models.DecimalField(
        db_column="pre_school_fees",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Tuition for language/foundation preparatory study."),
    )
    preparation_included = models.BooleanField(
        default=False,
        help_text=_("Whether the quoted tuition includes preparatory study."),
    )
    quota = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Number of admission places available for this offering, when known."),
    )
    deadline = models.DateField(
        null=True,
        blank=True,
        help_text=_("Last date on which an application can be submitted for this offering."),
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(
        blank=True,
        help_text=_("Preserve source footnotes, exceptional charges, or ambiguous terms here."),
    )
    source = models.ForeignKey(
        UniversityCatalogueSource,
        on_delete=models.PROTECT,
        related_name="offerings",
        null=True,
        blank=True,
    )

    def clean(self):
        super().clean()
        errors = {}
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            errors["valid_until"] = _("Valid until cannot be earlier than valid from.")
        if self.source_id and self.program_id:
            source = self.source
            program = self.program
            if source is not None and source.university_id != program.university_id:
                errors["source"] = _(
                    "Catalogue source must belong to the offering program's university."
                )
        if errors:
            raise ValidationError(errors)

    @property
    def effective_tuition(self):
        return self.tuition_discounted or self.tuition

    def __str__(self):
        return f"{self.program} - {self.academic_year} - {self.semester}"
