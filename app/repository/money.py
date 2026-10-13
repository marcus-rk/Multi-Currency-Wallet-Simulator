"""Conversion between Decimal amounts and integer minor units (ADR-0004).

Only the repository layer stores money, so only it uses these helpers.
"""

from decimal import Decimal

from app.domain.enums import Currency


def to_minor_units(amount: Decimal, currency: Currency) -> int:
    """Convert an amount to a whole number of minor units, e.g. 10.50 DKK -> 1050."""
    scaled = amount.scaleb(currency.decimal_places)
    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"{amount} {currency.value} has more than {currency.decimal_places} decimal places"
        )
    return int(scaled)


def from_minor_units(units: int, currency: Currency) -> Decimal:
    """Convert a whole number of minor units to an amount, e.g. 1050 DKK -> 10.50."""
    return Decimal(units).scaleb(-currency.decimal_places)
