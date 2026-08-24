from __future__ import annotations

from phonenumbers.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import (
    NumberParseException,
    PhoneNumberFormat,
    format_number,
    is_possible_number,
    is_valid_number,
    parse,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def _prepare_phone_value(value: str) -> str:
    value = (value or "").strip()
    if value.startswith("00"):
        value = "+" + value[2:]
    return value


def parse_phone_number(value: str, region: str | None = None) -> PhoneNumber:
    """Parse and validate a phone number.

    If no region is supplied, the number must be in international form, for
    example ``+31612345678``. Numbers starting with ``00`` are accepted and
    normalized to ``+`` before parsing.
    """
    value = _prepare_phone_value(value)

    if not value:
        raise ValidationError(
            _("Enter a phone number."),
            code="invalid_phone",
        )

    try:
        phone = parse(value, region)
    except NumberParseException as exc:
        raise ValidationError(
            _("Enter a valid phone number, including the country code."),
            code="invalid_phone",
        ) from exc

    if not is_possible_number(phone):
        raise ValidationError(
            _("This phone number is not possible."),
            code="invalid_phone",
        )

    if not is_valid_number(phone):
        raise ValidationError(
            _("Enter a valid phone number."),
            code="invalid_phone",
        )

    return phone


def normalize_phone_number(value: str, region: str | None = None) -> str:
    """Return a validated phone number in E.164 format."""
    phone = parse_phone_number(value, region=region)
    return format_number(phone, PhoneNumberFormat.E164)


def validate_phone_number(value: str) -> None:
    """Django field validator for international phone numbers."""
    parse_phone_number(value)
