# JMeter Performance Tests (FX stubbed)

This folder contains a JMeter test plan that exercises a realistic API flow (create wallet → deposit → exchange → list transactions).

The test plan is designed to be deterministic by running the backend against a local FX stub.

## Files

- `wallet_api_load_stress_spike_fx_stubbed.jmx` — main test plan
- `load/`, `stress/`, `spike/` — saved evidence exports (CSV/PNG) + short notes

## Prereqs

- Python deps installed (for the FX stub): `pip install -r requirements.txt`
- Backend running on `http://127.0.0.1:8080`
- JMeter installed locally (GUI or CLI)
  - macOS (Homebrew): `brew install jmeter`

## Terminal 1: Start FX stub server

This provides deterministic FX rates.

```bash
python -m tests.e2e.fx_stub_server --port 8081 --usd-rate 2.0
```

## Terminal 2: Start backend in Docker (port 8080)

Build the image:

```bash
docker build -t wallet-sim:latest .
```

Run it on `8080` and point it at the FX stub.

macOS/Windows Docker Desktop note: use `host.docker.internal` to reach the host from inside the container.

```bash
docker run --rm \
  -p 8080:5000 \
  -e EXCHANGE_API_URL=http://host.docker.internal:8081 \
  -e DATABASE=/app/instance/perf_wallet.db \
  wallet-sim:latest
```

## Terminal 3: Run the JMeter test

```bash
jmeter
```

- Open: `tests/performance/jmeter/wallet_api_load_stress_spike_fx_stubbed.jmx`
- Click the green Start button