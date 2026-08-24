from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.agents.models import Agent
from apps.core.models import BaseModel
from apps.core.phone import normalize_phone_number
from apps.core.validators import validate_phone_number
from apps.geography.models import Country


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        help_text=_(
            "Authenticated account that owns/manages this student record. "
            "One account may manage multiple students."
        ),
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

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
    nationality = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="students_nationality",
    )
    gender = models.CharField(max_length=20, choices=Gender.choices)

    email = models.EmailField(blank=True)
    cell = models.CharField(max_length=20, blank=True, validators=[validate_phone_number])
    birthdate = models.DateField(null=True, blank=True)

    english_test_type = models.CharField(
        max_length=20,
        choices=EnglishTestType.choices,
        blank=True,
    )
    english_language_test_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    high_school_gpa = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_(
            "Student's final high-school grade or GPA in the original grading "
            "system, for example 17.5 on a 20-point scale or 3.5 on a 4-point scale."
        ),
    )
    high_school_gpa_scale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_(
            "Maximum value of the grading scale used for the high-school grade "
            "or GPA, for example 20, 4, 10, or 100."
        ),
    )

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

    def save(self, *args, **kwargs):
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


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


def student_document_upload_path(instance, filename):
    return f"students/{instance.student.id}/documents/{filename}"


class StudentDocument(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(upload_to=student_document_upload_path)
    short_description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.student} - {self.get_document_type_display()}"
