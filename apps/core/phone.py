import phonenumbers


def normalize_phone_number(value: str) -> str:
    try:
        phone = phonenumbers.parse(value, None)
    except phonenumbers.NumberParseException as exc:
        raise ValueError("Invalid phone number") from exc
    if not phonenumbers.is_valid_number(phone):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
