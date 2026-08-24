from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from apps.content.models import ContactSubmission
from apps.core.validators import normalize_phone_number, parse_phone_number


class PhoneValidationTests(TestCase):
    def test_valid_international_number(self):
        phone = parse_phone_number("+31612345678")
        self.assertTrue(phone.is_valid())

    def test_e164_normalization(self):
        self.assertEqual(
            normalize_phone_number("+31612345678"),
            "+31612345678",
        )

    def test_double_zero_prefix_is_normalized(self):
        self.assertEqual(
            normalize_phone_number("0031612345678"),
            "+31612345678",
        )

    def test_invalid_number_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            parse_phone_number("not-a-phone-number")


class ContactFormPhoneValidationTests(TestCase):
    def test_contact_form_accepts_valid_phone_number(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Example Student",
                "email": "student@example.com",
                "phone": "+31612345678",
                "subject": "Admissions question",
                "message": "I would like more information.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactSubmission.objects.count(), 1)

    def test_contact_form_returns_error_for_invalid_phone(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Example Student",
                "email": "student@example.com",
                "phone": "123",
                "subject": "Admissions question",
                "message": "I would like more information.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
