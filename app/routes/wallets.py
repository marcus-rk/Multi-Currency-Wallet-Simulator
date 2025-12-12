from decimal import Decimal
from flask import Blueprint, request, jsonify
from app.domain.enums import Currency
from app.domain.exceptions import WalletNotFoundError
from app.services import wallet_service

wallets_bp = Blueprint("wallets", __name__, url_prefix="/api/wallets")


def _serialize_wallet(wallet):
    return {
        "id": wallet.id,
        "currency": wallet.currency.value,
        "balance": str(wallet.balance),
        "status": wallet.status.value,
        "created_at": wallet.created_at.isoformat(),
        "updated_at": wallet.updated_at.isoformat(),
    }


def _serialize_transaction(tx):
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


def _parse_amount_and_currency(data):
    """
    Helper to parse amount and currency from request data.
    Returns (amount, currency, error_response).
    If error_response is not None, return it immediately.
    """
    if not data or "amount" not in data:
        return None, None, (jsonify({"error": "Missing amount"}), 400)

    try:
        amount = Decimal(str(data["amount"]))
    except (ValueError, TypeError):
        return None, None, (jsonify({"error": "Invalid amount"}), 400)

    currency = None
    if "currency" in data:
        try:
            currency = Currency(data["currency"])
        except ValueError:
            return None, None, (jsonify({"error": "Invalid currency"}), 400)

    return amount, currency, None


@wallets_bp.route("", methods=["POST"])
def create_wallet():
    data = request.get_json()
    if not data or "currency" not in data:
        return jsonify({"error": "Missing currency"}), 400

    try:
        currency = Currency(data["currency"])
    except ValueError:
        return jsonify({"error": "Invalid currency"}), 400

    wallet = wallet_service.create_wallet(currency)
    return jsonify(_serialize_wallet(wallet)), 201


@wallets_bp.route("", methods=["GET"])
def list_wallets():
    wallets = wallet_service.list_wallets()
    return jsonify([_serialize_wallet(w) for w in wallets]), 200


@wallets_bp.route("/<wallet_id>", methods=["GET"])
def get_wallet(wallet_id):
    try:
        wallet = wallet_service.get_wallet(wallet_id)
        return jsonify(_serialize_wallet(wallet)), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@wallets_bp.route("/<wallet_id>/deposit", methods=["POST"])
def deposit(wallet_id):
    data = request.get_json()
    amount, currency, error = _parse_amount_and_currency(data)
    if error:
        return error

    if not currency:
        return jsonify({"error": "Missing currency"}), 400

    try:
        wallet, transaction = wallet_service.deposit_money(wallet_id, amount, currency)
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    response = {
        "wallet": _serialize_wallet(wallet),
        "transaction": _serialize_transaction(transaction)
    }
    
    if transaction.error_code:
        return jsonify(response), 400
    
    return jsonify(response), 200


@wallets_bp.route("/<wallet_id>/withdraw", methods=["POST"])
def withdraw(wallet_id):
    data = request.get_json()
    amount, currency, error = _parse_amount_and_currency(data)
    if error:
        return error

    if not currency:
        return jsonify({"error": "Missing currency"}), 400

    try:
        wallet, transaction = wallet_service.withdraw_money(wallet_id, amount, currency)
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    response = {
        "wallet": _serialize_wallet(wallet),
        "transaction": _serialize_transaction(transaction)
    }

    if transaction.error_code:
        return jsonify(response), 400

    return jsonify(response), 200


@wallets_bp.route("/exchange", methods=["POST"])
def exchange():
    data = request.get_json()
    required = ["source_wallet_id", "target_wallet_id", "amount"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        amount = Decimal(str(data["amount"]))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    try:
        source, target, transaction = wallet_service.exchange_money(
            data["source_wallet_id"],
            data["target_wallet_id"],
            amount
        )
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    response = {
        "source_wallet": _serialize_wallet(source),
        "target_wallet": _serialize_wallet(target),
        "transaction": _serialize_transaction(transaction)
    }

    if transaction.error_code:
        return jsonify(response), 400

    return jsonify(response), 200


@wallets_bp.route("/<wallet_id>/transactions", methods=["GET"])
def list_transactions(wallet_id):
    try:
        transactions = wallet_service.list_transactions(wallet_id)
        return jsonify([_serialize_transaction(tx) for tx in transactions]), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
