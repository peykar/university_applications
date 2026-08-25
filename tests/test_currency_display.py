from decimal import Decimal

from django.test import SimpleTestCase

from apps.core.templatetags.currency import (
    currency_amount,
    currency_amount_full,
    currency_symbol,
)


class CurrencyDisplayTests(SimpleTestCase):
    def test_known_symbols(self):
        self.assertEqual(currency_symbol("USD"), "$")
        self.assertEqual(currency_symbol("EUR"), "€")
        self.assertEqual(currency_symbol("TRY"), "₺")
        self.assertEqual(currency_symbol("GBP"), "£")

    def test_unknown_currency_falls_back_to_iso_code(self):
        self.assertEqual(currency_symbol("AED"), "AED")

    def test_card_price_uses_symbol_only(self):
        self.assertEqual(currency_amount(Decimal("15000"), "USD"), "$15,000")
        self.assertEqual(currency_amount(Decimal("12500"), "EUR"), "€12,500")
        self.assertEqual(currency_amount(Decimal("8500"), "TRY"), "₺8,500")

    def test_detailed_price_uses_symbol_and_iso_code(self):
        self.assertEqual(
            currency_amount_full(Decimal("15000"), "USD"),
            "$15,000 USD",
        )
        self.assertEqual(
            currency_amount_full(Decimal("12500"), "EUR"),
            "€12,500 EUR",
        )
        self.assertEqual(
            currency_amount_full(Decimal("8500"), "TRY"),
            "₺8,500 TRY",
        )
