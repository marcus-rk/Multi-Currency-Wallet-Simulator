"""Black-box tests for each currency's minor unit (ADR-0004).

Technique: equivalence partitioning. Each supported currency is its own
partition; all of them have two decimal places (one øre or one cent).
"""

import pytest

from app.domain.enums import Currency


@pytest.mark.parametrize(
    "currency",
    [
        Currency.DKK,  # partition: Danish krone, minor unit øre
        Currency.EUR,  # partition: euro, minor unit cent
        Currency.USD,  # partition: US dollar, minor unit cent
    ],
)
def test_decimal_places_supported_currency_is_two(currency):
    # Arrange: one supported currency (from parametrize)

    # Act: read the number of decimal places it declares
    decimal_places = currency.decimal_places

    # Assert: two decimal places, as CONTEXT.md defines the minor unit
    assert decimal_places == 2
