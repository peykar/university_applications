import phonenumbers


def normalize_phone_number(value: str) -> str:
    phone = phonenumbers.parse(value, None)
    if not phonenumbers.is_valid_number(phone):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
