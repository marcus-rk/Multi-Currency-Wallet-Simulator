# app/service/exchange_service.py

from decimal import Decimal
from typing import Optional
from flask import current_app
import requests

from app.domain.enums import Currency
from app.domain.exceptions import ExchangeRateServiceError

# Documentation URL Frankfurter API: https://frankfurter.dev

SAME_CURRENCY_RATE: Decimal = Decimal("1.0")


def get_exchange_rate(
    source: Currency,
    target: Currency,
    explicit_rate: Optional[Decimal] = None,
) -> Decimal:
    """
    Get the exchange rate from source currency to target currency.
    
    **Returns:**
    - If explicit_rate is provided, just return it.
    - If source and target are the same, return 1.0.
    - Otherwise, call the Frankfurter API using:
        GET {EXCHANGE_API_URL}/latest?base={source}&symbols={target}
    """
    if explicit_rate is not None:
        return explicit_rate

    # Same currency → no conversion
    if source == target:
        return SAME_CURRENCY_RATE

    # Call external exchange rate API
    try:
        api_url = current_app.config["EXCHANGE_API_URL"]
        response = requests.get(
            f"{api_url}/latest",
            params={
                "base": source.value,     # e.g "DKK"
                "symbols": target.value,  # e.g "USD"
            },
            timeout=5, # seconds
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise ExchangeRateServiceError(f"Failed to fetch exchange rate: {exc}") from exc

    # Extract rate from response data
    try:
        rate_str = str(data["rates"][target.value])
        return Decimal(rate_str)
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"Unexpected exchange API response: {data}") from exc
