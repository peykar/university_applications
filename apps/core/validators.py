from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import PhoneNumber


def _prepare_phone_value(value: str) -> str:
    value = (value or "").strip()
    if value.startswith("00"):
        value = "+" + value[2:]
    return value


def parse_phone_number(
    value: str,
    region: str | None = None,
) -> PhoneNumber:
    """
    Parse and validate a phone number using django-phonenumber-field.

    This intentionally uses the package's public `PhoneNumber` API instead of
    importing implementation details from either `phonenumbers` or
    `phonenumberslite`.

    Without a region, users should provide an international number, e.g.
    `+31612345678`. A `00` international prefix is normalized to `+`.
    """
    value = _prepare_phone_value(value)

    if not value:
        raise ValidationError(
            _("Enter a phone number."),
            code="invalid_phone",
        )

    try:
        phone = PhoneNumber.from_string(
            phone_number=value,
            region=region,
        )
    except Exception as exc:
        raise ValidationError(
            _("Enter a valid phone number, including the country code."),
            code="invalid_phone",
        ) from exc

    if not phone.is_valid():
        raise ValidationError(
            _("Enter a valid phone number."),
            code="invalid_phone",
        )

    return phone


def normalize_phone_number(
    value: str,
    region: str | None = None,
) -> str:
    """Return a validated phone number in E.164 format."""
    return parse_phone_number(value, region=region).as_e164


def validate_phone_number(value: str) -> None:
    """Django model/form field validator."""
    parse_phone_number(value)
