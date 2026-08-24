from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.core.phone import normalize_phone_number
from apps.core.validators import validate_phone_number


def agent_document_upload_path(instance, filename):
    return f"agents/{instance.agent.id}/documents/{filename}"


class Agent(BaseModel):
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="agents/logos/", blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    cell = models.CharField(max_length=20, blank=True, validators=[validate_phone_number])
    landline = models.CharField(max_length=20, blank=True, validators=[validate_phone_number])

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="agents", blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="sub_agents")
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        errors = {}

        for field_name in ("cell", "landline"):
            value = getattr(self, field_name)
            if value:
                try:
                    setattr(self, field_name, normalize_phone_number(value))
                except ValueError as exc:
                    errors[field_name] = str(exc)

        ancestor = self.parent
        seen = {self.pk} if self.pk else set()
        while ancestor:
            if ancestor.pk in seen:
                errors["parent"] = _("Agent hierarchy cannot contain a cycle.")
                break
            seen.add(ancestor.pk)
            ancestor = ancestor.parent

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.cell:
            self.cell = normalize_phone_number(self.cell)
        if self.landline:
            self.landline = normalize_phone_number(self.landline)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name


class AgentDocument(BaseModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text=_("Internal description visible to staff users."))
    file = models.FileField(upload_to=agent_document_upload_path)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent.company_name} - {self.name}"
