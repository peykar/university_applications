from __future__ import annotations

from decimal import Decimal
from typing import Any

from django import template

register = template.Library()

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "TRY": "₺",
    "GBP": "£",
}


def currency_symbol(code: str | None) -> str:
    """Return a familiar symbol, falling back to the ISO code when unknown."""
    normalized = (code or "").strip().upper()
    return CURRENCY_SYMBOLS.get(normalized, normalized)


def _format_amount(value: Any) -> str:
    if value in (None, ""):
        return ""

    try:
        amount = Decimal(str(value))
    except Exception:
        return str(value)

    if amount == amount.to_integral():
        return f"{int(amount):,}"

    formatted = f"{amount:,.2f}"
    return formatted.rstrip("0").rstrip(".")


@register.filter(name="currency_amount")
def currency_amount(value: Any, code: str | None) -> str:
    """
    Compact consumer-facing price, e.g. "$15,000" or "€12,500".

    Use this on programme/catalogue cards.
    """
    amount = _format_amount(value)
    if not amount:
        return ""

    symbol = currency_symbol(code)
    return f"{symbol}{amount}" if symbol else amount


@register.filter(name="currency_amount_full")
def currency_amount_full(value: Any, code: str | None) -> str:
    """
    Detailed financial price, e.g. "$15,000 USD" or "€12,500 EUR".

    Use this where the exact currency must be unambiguous.
    """
    amount = _format_amount(value)
    normalized = (code or "").strip().upper()
    if not amount:
        return ""

    symbol = currency_symbol(normalized)
    compact = f"{symbol}{amount}" if symbol else amount
    return f"{compact} {normalized}".strip()
