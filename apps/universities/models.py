from decimal import Decimal
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
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


class Intake(BaseModel, ActiveMixin):
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="intakes", null=True, blank=True
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name="intakes"
    )
    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100, blank=True)
    name_tr = models.CharField(max_length=100, blank=True)
    name_ar = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    application_open = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)

    def clean(self):
        super().clean()
        if (
            self.application_open
            and self.application_deadline
            and self.application_deadline < self.application_open
        ):
            raise ValidationError(
                {"application_deadline": _("Application deadline cannot precede opening date.")}
            )

    def __str__(self):
        return f"{self.academic_year} — {self.name_en}"


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

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=("slug_en",),
                condition=~models.Q(slug_en=""),
                name="uniq_program_slug_en",
            ),
            models.UniqueConstraint(
                fields=("slug_fa",),
                condition=~models.Q(slug_fa=""),
                name="uniq_program_slug_fa",
            ),
            models.UniqueConstraint(
                fields=("slug_tr",),
                condition=~models.Q(slug_tr=""),
                name="uniq_program_slug_tr",
            ),
            models.UniqueConstraint(
                fields=("slug_ar",),
                condition=~models.Q(slug_ar=""),
                name="uniq_program_slug_ar",
            ),
        ]

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
    internal_notes = models.TextField(
        blank=True,
        help_text=_(
            "Internal staff/import notes. Never expose this field on public or "
            "customer-facing surfaces."
        ),
    )

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
    duration_months = models.PositiveSmallIntegerField(null=True, blank=True)
    listing_priority = models.IntegerField(
        default=0,
        db_index=True,
        help_text=_(
            "Internal priority used to influence this item's position in listings. "
            "Higher values receive greater priority."
        ),
    )

    def _populate_missing_slugs(self) -> set[str]:
        """Rebuild localized public slugs from canonical structured Program data.

        A Program public slug is derived from the localized University slug,
        localized Academic Unit and Department when present, localized Program
        name, degree, thesis type when applicable, and the structured
        instruction-language variant. Historical/manual Program slug text is
        never used as an input to canonical generation.
        """
        populated: set[str] = set()
        if not self.university_id:
            return populated
        university = self.university
        language_rows = self._slug_instruction_language_rows()
        for locale in ("en", "fa", "tr", "ar"):
            field_name = f"slug_{locale}"
            university_slug = str(getattr(university, field_name, "") or "").strip()
            name = str(getattr(self, f"name_{locale}", "") or "").strip()
            if not university_slug or not name or not self.degree:
                continue
            name_slug = slugify(name, allow_unicode=locale != "en")
            if not name_slug:
                continue
            parts = [university_slug]
            academic_unit_token = self._related_slug_token(self.academic_unit, locale)
            if academic_unit_token:
                parts.append(academic_unit_token)
            department_token = self._related_slug_token(self.department, locale)
            if department_token:
                parts.append(department_token)
            parts.extend([name_slug, self._degree_slug_token(locale)])
            thesis_token = self._thesis_slug_token()
            if thesis_token:
                parts.append(thesis_token)
            language_tokens = self._instruction_language_slug_tokens(language_rows, locale)
            parts.extend(language_tokens)
            canonical = "-".join(part for part in parts if part)
            if getattr(self, field_name, "") != canonical:
                setattr(self, field_name, canonical)
                populated.add(field_name)
        return populated

    def _slug_instruction_language_rows(self):
        """Return instruction languages in deterministic public-slug order."""
        if not self.pk:
            return []
        return list(
            self.instruction_language_rows.select_related("language").order_by(
                "-is_primary", "language__slug_en", "language__name_en"
            )
        )

    @staticmethod
    def _related_slug_token(related, locale: str) -> str:
        """Return a localized Academic Unit/Department token when present."""
        if related is None:
            return ""
        token = str(getattr(related, f"slug_{locale}", "") or "").strip()
        if token:
            return token
        name = str(getattr(related, f"name_{locale}", "") or "").strip()
        return slugify(name, allow_unicode=locale != "en") if name else ""

    def _degree_slug_token(self, locale: str) -> str:
        """Return the canonical localized degree token used in public slugs."""
        tokens: dict[str, dict[str, str]] = {
            "en": {
                str(DegreeType.ASSOCIATE): "associate",
                str(DegreeType.BACHELOR): "bachelor",
                str(DegreeType.MASTER): "master",
                str(DegreeType.PHD): "phd",
            },
            "fa": {
                str(DegreeType.ASSOCIATE): "کاردانی",
                str(DegreeType.BACHELOR): "کارشناسی",
                str(DegreeType.MASTER): "کارشناسی-ارشد",
                str(DegreeType.PHD): "دکتری",
            },
            "tr": {
                str(DegreeType.ASSOCIATE): "ön-lisans",
                str(DegreeType.BACHELOR): "lisans",
                str(DegreeType.MASTER): "yüksek-lisans",
                str(DegreeType.PHD): "doktora",
            },
            "ar": {
                str(DegreeType.ASSOCIATE): "دبلوم",
                str(DegreeType.BACHELOR): "بكالوريوس",
                str(DegreeType.MASTER): "ماجستير",
                str(DegreeType.PHD): "دكتوراه",
            },
        }
        return tokens.get(locale, tokens["en"]).get(self.degree, str(self.degree))

    def _thesis_slug_token(self) -> str:
        if self.thesis_type == ThesisType.THESIS:
            return "thesis"
        if self.thesis_type == ThesisType.NON_THESIS:
            return "non-thesis"
        return ""

    @staticmethod
    def _instruction_language_slug_tokens(language_rows, locale: str) -> list[str]:
        """Return localized tokens for every structured instruction language."""
        tokens: list[str] = []
        for row in language_rows:
            language = row.language
            token = str(getattr(language, f"slug_{locale}", "") or "").strip()
            if not token:
                localized_name = str(
                    getattr(language, f"name_{locale}", "") or language.name_en or ""
                ).strip()
                token = slugify(localized_name, allow_unicode=locale != "en")
            if token and token not in tokens:
                tokens.append(token)
        return tokens

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.program.save()

    def delete(self, *args, **kwargs):
        program = self.program
        result = super().delete(*args, **kwargs)
        program.save()
        return result

    def __str__(self):
        return f"{self.program} — {self.language}"


class Currency(models.TextChoices):
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    TRY = "TRY", _("Turkish Lira")


class FeeBasis(models.TextChoices):
    ANNUAL = "annual", _("Annual")
    SEMESTER = "semester", _("Per semester")
    WHOLE_PROGRAM = "whole_program", _("Total (Whole Program)")
    PER_CREDIT = "per_credit", _("Per credit")
    ONE_TIME = "one_time", _("One time")


class OfferingFeeType(models.TextChoices):
    TUITION = "tuition", _("Tuition / list fee")
    DISCOUNTED_TUITION = "discounted_tuition", _("Discounted tuition")
    ADVANCE_PAYMENT = "advance_payment", _("Advance payment")
    CASH_PAYMENT = "cash_payment", _("Cash payment")
    INSTALLMENT_TOTAL = "installment_total", _("Installment total")
    DEPOSIT = "deposit", _("Deposit")
    PREPARATORY = "preparatory", _("Preparatory / foundation tuition")
    APPLICATION = "application", _("Application fee")
    REGISTRATION = "registration", _("Registration fee")
    OTHER = "other", _("Other")


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
    intake = models.ForeignKey(
        Intake,
        on_delete=models.PROTECT,
        related_name="program_offerings",
        help_text=_("Canonical intake. Fall/Spring/Academic Intake are intake names."),
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
        if self.intake_id and self.program_id:
            intake = self.intake
            program = self.program
            if intake is not None and intake.university_id not in (None, program.university_id):
                errors["intake"] = _("Intake must belong to the offering program's university.")
            if intake is not None and intake.academic_year_id != self.academic_year_id:
                errors["intake"] = _("Intake academic year must match the offering academic year.")
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
    def intake_name(self):
        """Canonical intake label for UI/API consumers."""
        return self.intake.name_en if self.intake_id and self.intake is not None else ""

    @property
    def display_tuition_fee(self):
        """Return the canonical payable/list tuition fee for presentation."""
        prefetched = getattr(self, "active_structured_fees", None)
        fees = (
            list(prefetched) if prefetched is not None else list(self.fees.filter(is_active=True))
        )
        for fee_type in (OfferingFeeType.DISCOUNTED_TUITION, OfferingFeeType.TUITION):
            for fee in fees:
                if fee.fee_type == fee_type and fee.amount is not None:
                    return fee
        return None

    @property
    def display_fees(self):
        """Canonical active structured fees in stable business-readable order."""
        prefetched = getattr(self, "active_structured_fees", None)
        fees = (
            list(prefetched) if prefetched is not None else list(self.fees.filter(is_active=True))
        )
        order = {
            OfferingFeeType.TUITION: 10,
            OfferingFeeType.DISCOUNTED_TUITION: 20,
            OfferingFeeType.ADVANCE_PAYMENT: 30,
            OfferingFeeType.CASH_PAYMENT: 40,
            OfferingFeeType.INSTALLMENT_TOTAL: 50,
            OfferingFeeType.DEPOSIT: 60,
            OfferingFeeType.PREPARATORY: 70,
            OfferingFeeType.APPLICATION: 80,
            OfferingFeeType.REGISTRATION: 90,
            OfferingFeeType.OTHER: 100,
        }
        return sorted(fees, key=lambda fee: (order.get(fee.fee_type, 999), fee.label, str(fee.pk)))

    def __str__(self):
        return f"{self.program} - {self.academic_year} - {self.intake.name_en}"


class OfferingFee(BaseModel, ActiveMixin):
    offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE, related_name="fees")
    fee_type = models.CharField(max_length=30, choices=OfferingFeeType.choices)
    label = models.CharField(max_length=255, blank=True)
    language = models.ForeignKey(
        ProgramLanguage,
        on_delete=models.PROTECT,
        related_name="offering_fees",
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=3, choices=Currency.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    basis = models.CharField(max_length=30, choices=FeeBasis.choices, default=FeeBasis.ANNUAL)
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.amount is None and self.percentage is None:
            raise ValidationError(_("A fee must define an amount, a percentage, or both."))
        if self.fee_type == OfferingFeeType.PREPARATORY and self.language_id is None:
            # A generic preparatory fee remains valid when the source does not name a language.
            return

    def __str__(self):
        return f"{self.offering} — {self.get_fee_type_display()}"
