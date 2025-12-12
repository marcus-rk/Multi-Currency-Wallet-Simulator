from flask import Blueprint, request, jsonify
from app.domain.enums import Currency
from app.domain.exceptions import WalletNotFoundError
from app.services import wallet_service
from app.routes.helpers import serialize_wallet

wallets_bp = Blueprint("wallets", __name__, url_prefix="/api/wallets")


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
    return jsonify(serialize_wallet(wallet)), 201


@wallets_bp.route("", methods=["GET"])
def list_wallets():
    wallets = wallet_service.list_wallets()
    return jsonify([serialize_wallet(w) for w in wallets]), 200


@wallets_bp.route("/<wallet_id>", methods=["GET"])
def get_wallet(wallet_id):
    try:
        wallet = wallet_service.get_wallet(wallet_id)
        return jsonify(serialize_wallet(wallet)), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404

