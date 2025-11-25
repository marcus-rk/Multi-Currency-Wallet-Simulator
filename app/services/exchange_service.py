# app/service/exchange_service.py

from decimal import Decimal
from typing import Optional

from app.domain.enums import Currency


def get_exchange_rate(
    source: Currency,
    target: Currency,
    explicit_rate: Optional[Decimal] = None,
) -> Decimal:
    """
    Exchange rate boundary.

    Supports three scenarios:

    1) The caller already has an exchange rate (e.g. from an external API
       or from a test):
         - Pass it as `explicit_rate` and it will be returned directly.

    2) Same-currency exchange:
         - If source == target, returns 1.0.

    3) Real external integration (not implemented here):
         - If currencies differ and no explicit_rate is given, this is the
           place where an HTTP call to an external exchange-rate API would
           be implemented.
         - For now, we raise NotImplementedError so missing integration is
           visible and not silently ignored.
    """
    # Case 1: caller already gave us a rate (e.g. from an external API)
    if explicit_rate is not None:
        return explicit_rate

    # Case 2: same currency → no conversion needed
    if source == target:
        return Decimal("1.0")

    # Case 3: this is where a real external API call would go.
    # Example (not implemented):
    #   response = requests.get(EXCHANGE_API_URL, params={...})
    #   data = response.json()
    #   return Decimal(str(data["rate"]))
    raise NotImplementedError(
        f"Exchange rate lookup for {source.value}/{target.value} "
        "requires an explicit rate or an external API integration."
    )
