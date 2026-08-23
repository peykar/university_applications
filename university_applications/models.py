from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .validators import normalize_phone_number, validate_phone_number


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    cell = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_phone_number],
        help_text=_("International format, e.g. +31612345678."),
    )
    cell_verified_at = models.DateTimeField(null=True, blank=True)
    telegram = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Telegram username without @."),
    )
    telegram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["username"]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.username

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
        if self.telegram:
            self.telegram = self.telegram.lstrip("@")
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        else:
            self.cell = None

    @property
    def is_cell_verified(self) -> bool:
        return bool(self.cell and self.cell_verified_at)

    def save(self, *args, **kwargs):
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        else:
            self.cell = None
        return super().save(*args, **kwargs)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        abstract = True


class LocalizedNameMixin(models.Model):
    name_en = models.CharField(max_length=255)
    name_fa = models.CharField(max_length=255, blank=True)
    name_tr = models.CharField(max_length=255, blank=True)
    name_ar = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name_en


class LocalizedSlugMixin(models.Model):
    slug_en = models.SlugField(max_length=255)
    slug_fa = models.SlugField(max_length=255, blank=True)
    slug_tr = models.SlugField(max_length=255, blank=True)
    slug_ar = models.SlugField(max_length=255, blank=True)

    class Meta:
        abstract = True


class LocalizedDescriptionMixin(models.Model):
    description_en = models.TextField(blank=True)
    description_fa = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Agent(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_profile",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_agents",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Agent")
        verbose_name_plural = _("Agents")

    def __str__(self) -> str:
        return f"Agent: {self.user}"

    def clean(self):
        super().clean()
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError({"parent": _("An agent cannot be its own parent.")})
        ancestor = self.parent
        visited = {self.id}
        while ancestor is not None:
            if ancestor.id in visited:
                raise ValidationError({"parent": _("Agent hierarchy cannot contain a cycle.")})
            visited.add(ancestor.id)
            ancestor = ancestor.parent


class Country(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    iso2 = models.CharField(max_length=2, unique=True, blank=True)
    iso3 = models.CharField(max_length=3, unique=True, blank=True)

    class Meta:
        ordering = ["name_en"]
        verbose_name_plural = _("Countries")


class Province(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="provinces")

    class Meta:
        ordering = ["country__name_en", "name_en"]
        constraints = [
            models.UniqueConstraint(fields=["country", "slug_en"], name="uniq_province_country_slug_en")
        ]


class City(BaseModel, LocalizedNameMixin, LocalizedSlugMixin, ActiveMixin):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name="cities")

    class Meta:
        ordering = ["province__country__name_en", "province__name_en", "name_en"]
        constraints = [
            models.UniqueConstraint(fields=["province", "slug_en"], name="uniq_city_province_slug_en")
        ]

    @property
    def country(self) -> Country:
        return self.province.country


class UniversityType(models.TextChoices):
    PUBLIC = "public", _("Public")
    PRIVATE = "private", _("Private")


class University(
    BaseModel,
    LocalizedNameMixin,
    LocalizedSlugMixin,
    LocalizedDescriptionMixin,
    ActiveMixin,
):
    logo = models.ImageField(upload_to="universities/logos/", blank=True)
    banner = models.ImageField(upload_to="universities/banners/", blank=True)
    website = models.URLField(blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="universities")
    university_type = models.CharField(max_length=20, choices=UniversityType.choices)
    is_yok_recognized = models.BooleanField(default=False)
    is_moe_approved = models.BooleanField(default=False)
    is_moh_approved = models.BooleanField(default=False)
    has_erasmus = models.BooleanField(default=False)
    has_dormitory = models.BooleanField(default=False)
    ranking_qs = models.PositiveIntegerField(null=True, blank=True)
    ranking_the = models.PositiveIntegerField(null=True, blank=True)
    ranking_arwu = models.PositiveIntegerField(null=True, blank=True)
    ranking_urap = models.PositiveIntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["name_en"]
        constraints = [models.UniqueConstraint(fields=["city", "slug_en"], name="uniq_university_city_slug_en")]


def university_media_upload_path(instance: "UniversityMedia", filename: str) -> str:
    return f"universities/{instance.university_id}/media/{Path(filename).name}"


class UniversityMedia(BaseModel):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="media")
    image = models.ImageField(upload_to=university_media_upload_path)
    title = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return self.title or f"Media for {self.university}"


class Department(
    BaseModel,
    LocalizedNameMixin,
    LocalizedSlugMixin,
    LocalizedDescriptionMixin,
    ActiveMixin,
):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="departments")

    class Meta:
        ordering = ["university__name_en", "name_en"]
        constraints = [
            models.UniqueConstraint(fields=["university", "slug_en"], name="uniq_department_university_slug_en")
        ]


class ProgramLanguage(
    BaseModel,
    LocalizedNameMixin,
    LocalizedSlugMixin,
    LocalizedDescriptionMixin,
    ActiveMixin,
):
    code = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ["name_en"]
        constraints = [models.UniqueConstraint(fields=["slug_en"], name="uniq_program_language_slug_en")]


class AcademicYear(BaseModel, LocalizedNameMixin, ActiveMixin):
    name_en = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50, blank=True)
    name_tr = models.CharField(max_length=50, blank=True)
    name_ar = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["-name_en"]
        constraints = [models.UniqueConstraint(fields=["name_en"], name="uniq_academic_year_name_en")]


class Semester(BaseModel, LocalizedNameMixin, ActiveMixin):
    name_en = models.CharField(max_length=100)
    name_fa = models.CharField(max_length=100, blank=True)
    name_tr = models.CharField(max_length=100, blank=True)
    name_ar = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name_en"]
        constraints = [models.UniqueConstraint(fields=["name_en"], name="uniq_semester_name_en")]


class DegreeType(models.TextChoices):
    ASSOCIATE = "associate", _("Associate")
    BACHELOR = "bachelor", _("Bachelor")
    MASTER = "master", _("Master")
    PHD = "phd", _("PhD")


class ThesisType(models.TextChoices):
    THESIS = "thesis", _("With Thesis")
    NON_THESIS = "non_thesis", _("Without Thesis")


class Program(
    BaseModel,
    LocalizedNameMixin,
    LocalizedSlugMixin,
    LocalizedDescriptionMixin,
    ActiveMixin,
):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="programs")
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="programs",
        null=True,
        blank=True,
    )
    degree = models.CharField(max_length=20, choices=DegreeType.choices)
    thesis_type = models.CharField(
        max_length=20,
        choices=ThesisType.choices,
        null=True,
        blank=True,
    )
    program_language = models.ForeignKey(
        ProgramLanguage,
        on_delete=models.PROTECT,
        related_name="programs",
    )
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    is_moe_approved = models.BooleanField(default=False)
    is_moh_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["university__name_en", "name_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["university", "slug_en", "degree", "program_language"],
                name="uniq_program_identity",
            ),
            models.CheckConstraint(
                condition=Q(thesis_type__isnull=True) | Q(degree__in=[DegreeType.MASTER, DegreeType.PHD]),
                name="thesis_only_for_postgraduate",
            ),
        ]

    def clean(self):
        super().clean()
        if self.department_id and self.department.university_id != self.university_id:
            raise ValidationError({"department": _("Department must belong to the program university.")})
        if self.thesis_type and self.degree not in {DegreeType.MASTER, DegreeType.PHD}:
            raise ValidationError({"thesis_type": _("Thesis type is only valid for Master's or PhD programs.")})


class Currency(models.TextChoices):
    USD = "USD", _("US Dollar")
    EUR = "EUR", _("Euro")
    TRY = "TRY", _("Turkish Lira")


class FeeBasis(models.TextChoices):
    ANNUAL = "annual", _("Annual")
    WHOLE_PROGRAM = "whole_program", _("Total (Whole Program)")


class ProgramOffering(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="offerings")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="program_offerings",
    )
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name="program_offerings")
    fee_basis = models.CharField(max_length=30, choices=FeeBasis.choices)
    currency = models.CharField(max_length=3, choices=Currency.choices)
    tuition = models.DecimalField(max_digits=12, decimal_places=2)
    tuition_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tuition_discounted = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cash_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tuition_cash = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tuition_annual_installment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pre_school_fees = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quota = models.PositiveIntegerField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-academic_year__name_en", "semester__name_en", "program__name_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["program", "academic_year", "semester"],
                name="uniq_program_offering_intake",
            )
        ]

    def __str__(self) -> str:
        return f"{self.program} — {self.academic_year} / {self.semester}"


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")


class EnglishTestType(models.TextChoices):
    TOEFL = "toefl", _("TOEFL")
    IELTS = "ielts", _("IELTS")
    PTE = "pte", _("PTE")
    CAMBRIDGE = "cambridge", _("Cambridge")
    OTHER = "other", _("Other")


class Student(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150)
    country_of_birth = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="students_born",
    )
    nationality = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="students_nationality")
    gender = models.CharField(max_length=20, choices=Gender.choices)
    email = models.EmailField(blank=True)
    cell = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
        help_text=_("International format, e.g. +905321234567."),
    )
    birthdate = models.DateField(null=True, blank=True)
    english_test_type = models.CharField(max_length=20, choices=EnglishTestType.choices, blank=True)
    english_language_test_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    high_school_gpa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    high_school_gpa_scale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    father_name = models.CharField(max_length=255, blank=True)
    mother_name = models.CharField(max_length=255, blank=True)
    passport_no = models.CharField(max_length=100, blank=True, db_index=True)
    passport_issuing_authority = models.CharField(max_length=255, blank=True)
    passport = models.FileField(upload_to="students/passports/", blank=True)
    passport_date_of_issue = models.DateField(null=True, blank=True)
    passport_date_of_expiry = models.DateField(null=True, blank=True)
    country_of_residence = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="students_residing",
    )
    city_of_residence = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("City of residence as free text."),
    )
    address = models.TextField(blank=True)
    educational_background = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return " ".join(part for part in [self.first_name, self.middle_name, self.last_name] if part)

    def clean(self):
        super().clean()
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        if self.passport_date_of_issue and self.passport_date_of_expiry:
            if self.passport_date_of_expiry <= self.passport_date_of_issue:
                raise ValidationError({"passport_date_of_expiry": _("Passport expiry must be after the issue date.")})

    def save(self, *args, **kwargs):
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        return super().save(*args, **kwargs)


class DocumentType(models.TextChoices):
    PASSPORT_COPY = "passport_copy", _("Passport Copy")
    PASSPORT_PHOTO = "passport_photo", _("Passport Size Photo")
    ID_CARD = "id_card", _("ID Card")
    DIPLOMA = "diploma", _("Diploma")
    TRANSCRIPT = "transcript", _("Transcript")
    TURKISH_PROFICIENCY = "turkish_proficiency", _("Turkish Proficiency Certificate")
    LANGUAGE_CERTIFICATE = "language_certificate", _("Language Certificate")
    YOK_RECOGNITION = "yok_recognition", _("YÖK Recognition Certificate")
    YOK_EQUIVALENCY = "yok_equivalency", _("YÖK Equivalency Certificate")
    OTHER = "other", _("Other")


def student_document_upload_path(instance: "StudentDocument", filename: str) -> str:
    return f"students/{instance.student_id}/documents/{Path(filename).name}"


class StudentDocument(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to=student_document_upload_path)
    short_description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["student", "document_type", "created_at"]

    def __str__(self) -> str:
        return f"{self.student} — {self.get_document_type_display()}"


class ApplicationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    UNDER_REVIEW = "under_review", _("Under Review")
    ADDITIONAL_DOCUMENTS = "additional_documents", _("Additional Documents Required")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    WITHDRAWN = "withdrawn", _("Withdrawn")
    CANCELLED = "cancelled", _("Cancelled")


class Application(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="applications")
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.PROTECT, related_name="applications")
    status = models.CharField(max_length=30, choices=ApplicationStatus.choices, default=ApplicationStatus.DRAFT)
    tuition = models.DecimalField(max_digits=12, decimal_places=2)
    deposit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.student} → {self.program_offering}"


class ApplicationDocument(BaseModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="documents")
    student_document = models.ForeignKey(
        StudentDocument,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    is_required = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["application", "student_document"],
                name="uniq_document_per_application",
            )
        ]

    def __str__(self) -> str:
        return f"{self.application} — {self.student_document}"

    def clean(self):
        super().clean()
        if self.application_id and self.student_document_id:
            if self.application.student_id != self.student_document.student_id:
                raise ValidationError(
                    {"student_document": _("The document must belong to the application's student.")}
                )
