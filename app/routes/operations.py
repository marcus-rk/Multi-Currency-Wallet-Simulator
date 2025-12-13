from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify
from app.domain.exceptions import WalletNotFoundError, ExchangeRateServiceError
from app.services import wallet_service
from app.routes.helpers import serialize_wallet, serialize_transaction, parse_amount_and_currency

operations_bp = Blueprint("operations", __name__, url_prefix="/api/wallets")

@operations_bp.route("/<wallet_id>/deposit", methods=["POST"])
def deposit(wallet_id):
    data = request.get_json()
    amount, currency, error = parse_amount_and_currency(data)
    if error:
        return jsonify(error[0]), error[1]

    if not currency:
        return jsonify({"error": "Missing currency"}), 400

    try:
        wallet, transaction = wallet_service.deposit_money(wallet_id, amount, currency)
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    response = {
        "wallet": serialize_wallet(wallet),
        "transaction": serialize_transaction(transaction)
    }
    
    if transaction.error_code:
        return jsonify(response), 422
    
    return jsonify(response), 200


@operations_bp.route("/<wallet_id>/withdraw", methods=["POST"])
def withdraw(wallet_id):
    data = request.get_json()
    amount, currency, error = parse_amount_and_currency(data)
    if error:
        return jsonify(error[0]), error[1]

    if not currency:
        return jsonify({"error": "Missing currency"}), 400

    try:
        wallet, transaction = wallet_service.withdraw_money(wallet_id, amount, currency)
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    response = {
        "wallet": serialize_wallet(wallet),
        "transaction": serialize_transaction(transaction)
    }

    if transaction.error_code:
        return jsonify(response), 422

    return jsonify(response), 200


@operations_bp.route("/exchange", methods=["POST"])
def exchange():
    data = request.get_json()
    required = ["source_wallet_id", "target_wallet_id", "amount"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        amount = Decimal(str(data["amount"]))
    except (ValueError, TypeError, InvalidOperation):
        return jsonify({"error": "Invalid amount"}), 400

    try:
        source, target, transaction = wallet_service.exchange_money(
            data["source_wallet_id"],
            data["target_wallet_id"],
            amount
        )
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ExchangeRateServiceError as e:
        return jsonify({"error": str(e)}), 502

    response = {
        "source_wallet": serialize_wallet(source),
        "target_wallet": serialize_wallet(target),
        "transaction": serialize_transaction(transaction)
    }

    if transaction.error_code:
        return jsonify(response), 422

    return jsonify(response), 200
