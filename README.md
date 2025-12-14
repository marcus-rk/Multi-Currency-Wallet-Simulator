[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Embedded%20DB-lightgrey.svg)](https://www.sqlite.org/index.html)
[![Pytest](https://img.shields.io/badge/Pytest-Testing-orange.svg)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-E2E%20Tests-purple.svg)](https://playwright.dev/)
[![JMeter](https://img.shields.io/badge/JMeter-Performance-red.svg)](https://jmeter.apache.org/)
[![CI](https://github.com/marcus-rk/Multi-Currency-Wallet-Simulator/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/marcus-rk/Multi-Currency-Wallet-Simulator/actions/workflows/ci.yml)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=marcus-rk_Multi-Currency-Wallet-Simulator&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=marcus-rk_Multi-Currency-Wallet-Simulator)

# Multi-Currency Wallet Simulator

A small backend-focused project that simulates a single-user multi-currency wallet with deposits, withdrawals, exchanges, and transaction history exposed through a REST API and a minimal HTML/JS frontend.

The project is designed as a **testing playground**: unit, integration, API, E2E (Playwright) and performance (JMeter) tests are first-class citizens, not an afterthought.

---

## Domain Concepts & Project Elements

This project is focused on making a small **multi-currency wallet simulator** for:

- **Managing wallets** – create wallets in different currencies and see their balances.
- **Moving money** – make deposits, withdrawals and currency exchanges between wallets.
- **Seeing history** – view a simple log of what happened to a wallet over time.
- **Using external API** – fetches live exchange rates to support currency conversions (tests use a local stub by setting `EXCHANGE_API_URL`).

---

## Project Structure (folders only)

```text
.
├── app/          # Flask application package (config, routes, services, repository, database helpers)
├── frontend/     # Static HTML/CSS/JS frontend (client-side rendering)
├── tests/        # Test suite (unit, integration, API, E2E, performance)
├── seed/         # seeding script
├── instance/     # Runtime data (SQLite DB files)
└── docs/         # SRS, test plan/report, diagrams, and other documentation
```

Top-level special files:

- `.gitignore` – ignore virtualenv, instance DB, test reports, etc.
- `.env` – local environment 
- `requirements.txt` – Python dependencies
- `README.md` – main project documentation (this file)

---

## Setup

Note: CI runs on Python 3.12, while the Docker image uses Python 3.11. Small output differences between environments can happen.

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Testing

Run all tests:

```bash
pytest
```

Run all tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Generate HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

---

Run unit tests only (fast):

```bash
pytest tests/unit
```

Run unit tests with coverage:

```bash
pytest tests/unit --cov=app --cov-report=term-missing
```

---

Run integration tests only (full stack, FX stubbed):

```bash
pytest -m integration
```

Run integration tests with coverage:

```bash
pytest -m integration --cov=app --cov-report=term-missing
```

---

## Seeding demo data (optional)

Seed demo wallets + transactions once (skips if already seeded): `python seed/seed_db.py`.
Reset and reseed from scratch: `python seed/seed_db.py --reset` (or clear tables with `--force`).
Docker (persist DB): run with `-v wallet-sim-data:/app/instance`, then seed once via `docker exec -it Currency-Wallet-Sim python seed/seed_db.py`.

---

## Docker (Build + Run)

Build the image:

```bash
docker build -t wallet-sim:latest .
```

Note: The Docker build ignores local `instance/*.db` files (via `.dockerignore`) and bakes a fresh seeded demo database into the image.

Run the container with a stable name:

```bash
docker run --name Currency-Wallet-Sim -p 8080:5000 wallet-sim:latest
```

Open the UI at:

- `http://127.0.0.1:8080/`

Open the API at:

- `http://127.0.0.1:8080/api/wallets`

If you pulled new changes, rebuild the image first:

```bash
docker build -t wallet-sim:latest .
```

Run detached (background):

```bash
docker run -d --name Currency-Wallet-Sim -p 8080:5000 wallet-sim:latest
```

Stop and remove (when running detached):

```bash
docker stop Currency-Wallet-Sim
docker rm Currency-Wallet-Sim
```

---

## 👥 Author

- **Marcus R. Kjærsgaard**  
  [![GitHub](https://img.shields.io/badge/GitHub-marcus--rk-black?logo=github)](https://github.com/marcus-rk)

---

... More to come ...
