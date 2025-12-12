from decimal import Decimal
from app.domain.enums import Currency

def serialize_wallet(wallet):
    return {
        "id": wallet.id,
        "currency": wallet.currency.value,
        "balance": str(wallet.balance),
        "status": wallet.status.value,
        "created_at": wallet.created_at.isoformat(),
        "updated_at": wallet.updated_at.isoformat(),
    }


def serialize_transaction(tx):
    return {
        "id": tx.id,
        "type": tx.type.value,
        "source_wallet_id": tx.source_wallet_id,
        "target_wallet_id": tx.target_wallet_id,
        "amount": str(tx.amount),
        "currency": tx.currency.value,
        "credited_amount": str(tx.credited_amount) if tx.credited_amount else None,
        "credited_currency": tx.credited_currency.value if tx.credited_currency else None,
        "status": tx.status.value,
        "error_code": tx.error_code.value if tx.error_code else None,
        "created_at": tx.created_at.isoformat(),
    }


def parse_amount_and_currency(data):
    """
    Helper to parse amount and currency from request data.
    Returns (amount, currency, error_tuple).
    If error_tuple is not None, it is ({error_dict}, status_code).
    """
    if not data or "amount" not in data:
        return None, None, ({"error": "Missing amount"}, 400)

    try:
        amount = Decimal(str(data["amount"]))
    except (ValueError, TypeError):
        return None, None, ({"error": "Invalid amount"}, 400)

    currency = None
    if "currency" in data:
        try:
            currency = Currency(data["currency"])
        except ValueError:
            return None, None, ({"error": "Invalid currency"}, 400)

    return amount, currency, None
