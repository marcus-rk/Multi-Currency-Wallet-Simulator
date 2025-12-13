from pathlib import Path
from flask import Blueprint, send_from_directory

frontend_bp = Blueprint("frontend", __name__)

_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
_FAVICON_PNG = "icons8-currency-exchange-48.png"
_MIME_PNG = "image/png"


@frontend_bp.route("/", methods=["GET"])
def frontend_index():
    return send_from_directory(_FRONTEND_DIR, "index.html")


@frontend_bp.route("/wallet.html", methods=["GET"])
def frontend_wallet():
    return send_from_directory(_FRONTEND_DIR, "wallet.html")


@frontend_bp.route("/exchange.html", methods=["GET"])
def frontend_exchange():
    return send_from_directory(_FRONTEND_DIR, "exchange.html")


@frontend_bp.route("/css/<path:filename>", methods=["GET"])
def frontend_css(filename: str):
    return send_from_directory(_FRONTEND_DIR / "css", filename)


@frontend_bp.route("/js/<path:filename>", methods=["GET"])
def frontend_js(filename: str):
    return send_from_directory(_FRONTEND_DIR / "js", filename)


@frontend_bp.route("/favicon.ico", methods=["GET"])
def frontend_favicon_ico():
    # Many user agents request /favicon.ico regardless of the HTML link tags.
    # We serve the same PNG used by the HTML pages to keep assets simple.
    return send_from_directory(_FRONTEND_DIR, _FAVICON_PNG, mimetype=_MIME_PNG)


@frontend_bp.route("/favicon.png", methods=["GET"])
def frontend_favicon_png():
    return send_from_directory(_FRONTEND_DIR, _FAVICON_PNG, mimetype=_MIME_PNG)
