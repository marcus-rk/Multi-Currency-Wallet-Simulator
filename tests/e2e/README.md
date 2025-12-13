# Playwright E2E (UI-only)

These tests exercise the app through the real browser UI (click/type/select only).

## Prereqs

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Quickstart (deterministic FX)

Run a tiny local FX stub server, then start the backend with `EXCHANGE_API_URL` pointed at it.

This keeps production code clean (no “test mode” branches) and still exercises the real HTTP + JSON parsing path.

### Terminal 1: Start FX stub server

```bash
python -m tests.e2e.fx_stub_server --port 8081 --usd-rate 2.0
```

### Terminal 2: Start backend pointing at stub

```bash
export EXCHANGE_API_URL=http://127.0.0.1:8081

# Optional: keep E2E data separate
export DATABASE=instance/e2e_wallet.db

python -m flask --app app run --port 5000
```

The UI is served by the backend, so this is all you need running.

### Terminal 3: Run E2E tests

Default base URL is `http://127.0.0.1:5000`.

```bash
pytest -m e2e tests/e2e/test_wallet_ui_e2e.py
```

### One-shot (copy/paste)

This starts the FX stub + backend, runs the tests, and then stops the processes.

```bash
set -euo pipefail

python -m tests.e2e.fx_stub_server --port 8081 --usd-rate 2.0 &
FX_PID=$!

export EXCHANGE_API_URL=http://127.0.0.1:8081
export DATABASE=instance/e2e_wallet.db

python -m flask --app app run --port 5000 &
APP_PID=$!

cleanup() { kill "$APP_PID" "$FX_PID" 2>/dev/null || true; }
trap cleanup EXIT

pytest -m e2e tests/e2e/test_wallet_ui_e2e.py
```

If you run via Docker (e.g. `-p 8080:5000`), point the tests at that port:

```bash
export E2E_BASE_URL=http://127.0.0.1:8080
pytest -m e2e tests/e2e/test_wallet_ui_e2e.py
```

### Docker note (important)

If the backend runs inside Docker, `http://127.0.0.1:8081` (or `localhost`) points to the container itself, not your host.

- macOS/Windows Docker Desktop: use `http://host.docker.internal:8081`
- Docker Compose: run the stub as a service and use `http://fx-stub:8081`

## Notes

- Tests create their own wallets and locate them by the wallet id shown in the UI.
- No API helpers or DB assertions are used; assertions are user-visible (balances, transaction rows, wallet status).
