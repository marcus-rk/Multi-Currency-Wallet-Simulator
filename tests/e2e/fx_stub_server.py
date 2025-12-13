"""Test stub for deterministic FX during E2E.

Purpose
-------
The app normally calls an external FX provider (Frankfurter-like) over HTTP.
For UI E2E tests we want runs to be:
- deterministic (stable expected results),
- offline-friendly (no dependency on third-party uptime/rate limits),
- production-faithful (no "test mode" branches in application code).

This file provides a tiny HTTP server that mimics the subset of the Frankfurter
API shape used by the app.

Supported endpoint
------------------
- GET /latest?base=<CCY>&symbols=<CCY>[,<CCY>...]

Example:
    /latest?base=DKK&symbols=USD

Response shape (success)
------------------------
Returns JSON with the same top-level fields the real provider returns:

- amount: always 1.0
- base: normalized to uppercase
- date: fixed string for determinism (not used by the app)
- rates: mapping of requested symbol -> fixed float rate

Limitations
-----------
- Only supports the currencies needed by the E2E suite (USD/EUR by default).
- No other Frankfurter endpoints are implemented.
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


_FIXED_DATE = "2025-12-13"


def _parse_args() -> argparse.Namespace:
    # CLI makes it easy to run locally and in CI without editing code.
    parser = argparse.ArgumentParser(description="Frankfurter-shaped FX stub for E2E")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--usd-rate", default="2.0")
    parser.add_argument("--eur-rate", default="1.5")
    return parser.parse_args()


def _make_handler(*, usd_rate: float, eur_rate: float):
    # Configure supported targets up-front so request handling stays simple.
    rates_by_target = {
        "USD": usd_rate,
        "EUR": eur_rate,
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A002
            # Keep test output clean; pytest should show failures, not request logs.
            return

        def do_GET(self) -> None:  # noqa: N802
            # Route dispatch: we only implement /latest.
            parsed = urlparse(self.path)
            if parsed.path != "/latest":
                self._send_json(404, {"error": "not found"})
                return

            # Query parsing and validation (Frankfurter-style).
            query = parse_qs(parsed.query)
            base = (query.get("base") or [""])[0]
            symbols_raw = (query.get("symbols") or [""])[0]

            if not base or not symbols_raw:
                self._send_json(400, {"error": "missing required query params: base, symbols"})
                return

            # Frankfurter accepts a single symbol or a comma-separated list.
            symbols = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()]
            if not symbols:
                self._send_json(400, {"error": "symbols must contain at least one currency"})
                return

            # Build the rates response; reject unsupported symbols to catch mistakes early.
            rates: dict[str, float] = {}
            for symbol in symbols:
                if symbol not in rates_by_target:
                    self._send_json(400, {"error": f"unsupported symbol: {symbol}"})
                    return
                rates[symbol] = float(rates_by_target[symbol])

            self._send_json(
                200,
                {
                    "amount": 1.0,
                    "base": base.upper(),
                    "date": _FIXED_DATE,
                    "rates": rates,
                },
            )

        def _send_json(self, status: int, body: dict) -> None:
            # Minimal JSON response helper.
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return Handler


def main() -> None:
    args = _parse_args()

    try:
        usd_rate = float(args.usd_rate)
        eur_rate = float(args.eur_rate)
    except ValueError as exc:
        raise SystemExit("usd-rate/eur-rate must be numeric") from exc

    handler_cls = _make_handler(usd_rate=usd_rate, eur_rate=eur_rate)
    server = HTTPServer((args.host, args.port), handler_cls)

    print(f"FX stub listening on http://{args.host}:{args.port} (USD={usd_rate}, EUR={eur_rate})")
    server.serve_forever()


if __name__ == "__main__":
    main()
