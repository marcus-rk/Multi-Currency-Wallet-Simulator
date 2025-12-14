from flask import Blueprint, request, jsonify
from app.domain.enums import Currency, WalletStatus
from app.domain.exceptions import WalletNotFoundError, WalletStateError
from app.services import wallet_service
from app.routes.helpers import serialize_wallet, serialize_transaction

wallets_bp = Blueprint("wallets", __name__, url_prefix="/api/wallets")


WALLET_TRANSITION_NOT_ALLOWED_ERROR = "Wallet state transition not allowed"
INTERNAL_SERVER_ERROR = "Internal server error"


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


@wallets_bp.route("/<wallet_id>/freeze", methods=["POST"])
def freeze_wallet(wallet_id):
    try:
        wallet, tx = wallet_service.change_wallet_status(wallet_id, WalletStatus.FROZEN)
        payload = {"wallet": serialize_wallet(wallet)}
        if tx is not None:
            payload["transaction"] = serialize_transaction(tx)
        return jsonify(payload), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except WalletStateError:
        return jsonify({"error": WALLET_TRANSITION_NOT_ALLOWED_ERROR}), 409


@wallets_bp.route("/<wallet_id>/unfreeze", methods=["POST"])
def unfreeze_wallet(wallet_id):
    try:
        wallet, tx = wallet_service.change_wallet_status(wallet_id, WalletStatus.ACTIVE)
        payload = {"wallet": serialize_wallet(wallet)}
        if tx is not None:
            payload["transaction"] = serialize_transaction(tx)
        return jsonify(payload), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except WalletStateError:
        return jsonify({"error": WALLET_TRANSITION_NOT_ALLOWED_ERROR}), 409


@wallets_bp.route("/<wallet_id>/close", methods=["POST"])
def close_wallet(wallet_id):
    try:
        wallet, tx = wallet_service.change_wallet_status(wallet_id, WalletStatus.CLOSED)
        payload = {"wallet": serialize_wallet(wallet)}
        if tx is not None:
            payload["transaction"] = serialize_transaction(tx)
        return jsonify(payload), 200
    except WalletNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except WalletStateError:
        return jsonify({"error": WALLET_TRANSITION_NOT_ALLOWED_ERROR}), 409


@wallets_bp.errorhandler(Exception)
def wallets_unexpected_error(_err):
    return jsonify({"error": INTERNAL_SERVER_ERROR}), 500

