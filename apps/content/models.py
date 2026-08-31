from django.db import models

from apps.core.localization import localized_value
from apps.core.models import BaseModel
from apps.core.phone import normalize_phone_number
from apps.core.validators import validate_phone_number


class FAQCategory(BaseModel):
    key = models.SlugField(max_length=100, unique=True, blank=True)
    name_en = models.CharField(max_length=255)
    name_fa = models.CharField(max_length=255, blank=True)
    name_tr = models.CharField(max_length=255, blank=True)
    name_ar = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def faq_count(self):
        return self.faqs.filter(is_active=True).count()

    @property
    def localized_name(self):
        return localized_value(self, "name")

    def __str__(self):
        return self.localized_name


class FAQ(BaseModel):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name="faqs")
    question_en = models.CharField(max_length=500)
    question_fa = models.CharField(max_length=500, blank=True)
    question_tr = models.CharField(max_length=500, blank=True)
    question_ar = models.CharField(max_length=500, blank=True)
    answer_en = models.TextField()
    answer_fa = models.TextField(blank=True)
    answer_tr = models.TextField(blank=True)
    answer_ar = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def localized_question(self):
        return localized_value(self, "question")

    @property
    def localized_answer(self):
        return localized_value(self, "answer")

    def __str__(self):
        return self.localized_question


class ContactSubmission(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True, validators=[validate_phone_number])
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    is_handled = models.BooleanField(default=False)
    handled_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone_number(self.phone)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.subject or self.name
