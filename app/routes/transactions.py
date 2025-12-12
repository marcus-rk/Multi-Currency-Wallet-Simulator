from flask import Blueprint, jsonify
from app.domain.exceptions import WalletNotFoundError
from app.services import wallet_service
from app.routes.helpers import serialize_transaction

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/wallets")

@transactions_bp.route("/<wallet_id>/transactions", methods=["GET"])
def list_transactions(wallet_id):
    try:
        transactions = wallet_service.list_transactions(wallet_id)
        return jsonify([serialize_transaction(tx) for tx in transactions]), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
