[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Embedded%20DB-lightgrey.svg)](https://www.sqlite.org/index.html)
[![Pytest](https://img.shields.io/badge/Pytest-Testing-orange.svg)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-E2E%20Tests-purple.svg)](https://playwright.dev/)
[![JMeter](https://img.shields.io/badge/JMeter-Performance-red.svg)](https://jmeter.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-Dockerfile-2496ED?logo=docker&logoColor=white)](#docker)
[![Postman](https://img.shields.io/badge/Postman-API%20Tests-FF6C37?logo=postman&logoColor=white)](tests/api_postman/README.md)
[![CI](https://github.com/marcus-rk/Multi-Currency-Wallet-Simulator/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/marcus-rk/Multi-Currency-Wallet-Simulator/actions/workflows/ci.yml)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=marcus-rk_Multi-Currency-Wallet-Simulator&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=marcus-rk_Multi-Currency-Wallet-Simulator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# Multi-Currency Wallet Simulator

A small backend-focused project that simulates a single-user multi-currency wallet with deposits, withdrawals, exchanges, and transaction history exposed through a REST API and a minimal HTML/JS frontend.

The project is designed as a **testing playground**: unit, integration, API, E2E (Playwright) and performance (JMeter) tests are first-class citizens, not an afterthought.

---

## Table of Contents

- [Quick Overview (for teachers)](#quick-overview)
- [One-minute Quickstart (local)](#quickstart)
- [Domain Concepts](#domain)
- [Runtime Configuration](#runtime-config)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Testing](#testing)
- [Seeding demo data](#seeding)
- [Docker (Build + Run)](#docker)
- [Notes](#notes)
- [Author](#author)

---

<a id="quick-overview"></a>

## Quick Overview (for teachers)

### Exam deliverables map

| Deliverable | Where it is in this repo |
|---|---|
| SRS (PDF) | [docs/SRS/Software Requirements Specification (SRS) v1-0.pdf](docs/SRS/Software%20Requirements%20Specification%20%28SRS%29%20v1-0.pdf), [docs/SRS/Software Requirements Specification (SRS) v2-1.pdf](docs/SRS/Software%20Requirements%20Specification%20%28SRS%29%20v2-1.pdf) |
| Review report (PDF) | [docs/SRS/review/Multi-Currency Wallet - Summary Review Report.pdf](docs/SRS/review/Multi-Currency%20Wallet%20-%20Summary%20Review%20Report.pdf) |
| Risk assessment (PDF) | [docs/Risk Assessment.pdf](docs/Risk%20Assessment.pdf) |
| Black-box test design (PDF) | [docs/Black-Box-Test-Design.pdf](docs/Black-Box-Test-Design.pdf) |
| Static testing + white-box + coverage (PDF) | [docs/Static-Testing-White-Box-Coverage.pdf](docs/Static-Testing-White-Box-Coverage.pdf) |
| CI output snapshots (txt) | [docs/ci_output](docs/ci_output) (see also [docs/ci_output/README.md](docs/ci_output/README.md)) |
| API testing (Postman) | [tests/api_postman](tests/api_postman) (collection + environment JSON + evidence screenshot) |
| E2E UI tests (Playwright) | [tests/e2e](tests/e2e) (tests + FX stub server + instructions) |
| Performance (JMeter) | [tests/performance/jmeter](tests/performance/jmeter) (JMX + load/stress/spike evidence) |
| UI performance evidence (Lighthouse) | [tests/performance/lighthouse](tests/performance/lighthouse) |
| Usability test design (PDF) | [docs/Usability-testing-design.pdf](docs/Usability-testing-design.pdf) |

### Ports & URLs

| Context | What | URL |
|---|---|---|
| Local | UI | `http://127.0.0.1:5000/` |
| Local | API | `http://127.0.0.1:5000/api/wallets` |
| Docker | UI | `http://127.0.0.1:8080/` |
| Docker | API | `http://127.0.0.1:8080/api/wallets` |
| Both | Health check | `/api/health/` |

### Key API endpoints (quick reference)

- `POST /api/wallets` (create wallet)
- `GET /api/wallets` (list wallets)
- `GET /api/wallets/<wallet_id>` (get wallet)
- `POST /api/wallets/<wallet_id>/deposit`
- `POST /api/wallets/<wallet_id>/withdraw`
- `POST /api/wallets/exchange`
- `GET /api/wallets/<wallet_id>/transactions`

---

<a id="quickstart"></a>

## One-minute Quickstart (local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run the app (UI + API)
flask --app app:create_app run --port 5000
```

See [Testing](#testing) for Postman, E2E (Playwright), and performance (JMeter) instructions.

<a id="domain"></a>

## Domain Concepts & Project Elements

This project is focused on making a small **multi-currency wallet simulator** for:

- **Managing wallets** – create wallets in different currencies and see their balances.
- **Moving money** – make deposits, withdrawals and currency exchanges between wallets.
- **Seeing history** – view a simple log of what happened to a wallet over time.
- **Using external API** – fetches live exchange rates to support currency conversions (tests use a local stub by setting `EXCHANGE_API_URL`).

<a id="runtime-config"></a>

## Runtime Configuration

Environment variables supported:

- `DATABASE` (default: `instance/wallet.db`) – SQLite DB path used by the app.
- `TEST_DATABASE` (default: `instance/test_wallet.db`) – DB path used by the test config.
- `EXCHANGE_API_URL` (default: `https://api.frankfurter.dev/v1`) – public FX API base URL.

Note: E2E (Playwright) and performance (JMeter) runs point EXCHANGE_API_URL to a local stub for deterministic results; production/default uses Frankfurter.

<a id="project-structure"></a>

## Project Structure

```text
.
├── app/               # Flask app package
│   ├── routes/        # HTTP API + static frontend routes (Flask blueprints)
│   ├── services/      # orchestration layer (domain + repos + external FX)
│   ├── repository/    # SQLite data access
│   ├── domain/        # pure business logic (models, rules, enums, exceptions)
│   ├── config.py
│   └── database.py
├── frontend/          # Static HTML/CSS/JS frontend (client-side rendering)
├── tests/             # Test suite
│   ├── unit/
│   ├── integration/
│   ├── api_postman/
│   ├── e2e/
│   └── performance/
├── seed/              # Seeding script(s)
├── instance/          # Runtime data (SQLite DB files)
└── docs/              # PDFs + CI output snapshots for exam deliverables
```

Top-level special files:

- `.gitignore` – ignore virtualenv, instance DB, test reports, etc.
- `.env` – optional local environment variables (do not commit secrets)
- `requirements.txt` – Python dependencies
- `README.md` – main project documentation (this file)

<a id="setup"></a>

## Setup

Note: CI runs on Python 3.12, while the Docker image uses Python 3.11. Small output differences between environments can happen.

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

<a id="testing"></a>

## Testing

Testing docs by type:

- Unit + integration philosophy: [tests/testing_approach_wallet_simulator.md](tests/testing_approach_wallet_simulator.md)
- API tests (Postman): [tests/api_postman/README.md](tests/api_postman/README.md)
- E2E (Playwright): [tests/e2e/README.md](tests/e2e/README.md)
- Performance (JMeter): [tests/performance/jmeter/README.md](tests/performance/jmeter/README.md)

### Quick commands

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

Run unit tests only (fast):

```bash
pytest tests/unit
```

Run unit tests with coverage:

```bash
pytest tests/unit --cov=app --cov-report=term-missing
```

Run integration tests only (full stack, FX stubbed):

```bash
pytest -m integration
```

Run integration tests with coverage:

```bash
pytest -m integration --cov=app --cov-report=term-missing
```

<a id="seeding"></a>

## Seeding demo data (optional)

Local (seed once; script will skip if already seeded):

```bash
python seed/seed_db.py
```

Local (reset + reseed from scratch):

```bash
python seed/seed_db.py --reset --force
```

Docker (persist DB using a named volume, then seed inside the container):

```bash
docker run -d --name Currency-Wallet-Sim -p 8080:5000 -v wallet-sim-data:/app/instance wallet-sim:latest
docker exec -it Currency-Wallet-Sim python seed/seed_db.py
```

---

<a id="docker"></a>

## Docker (Build + Run)

Build the image:

```bash
docker build -t wallet-sim:latest .
```

Note: The Docker build ignores local `instance/*.db` files (via `.dockerignore`) and bakes a fresh seeded demo database into the image.

Run the container with a stable name (foreground):

```bash
docker run --name Currency-Wallet-Sim -p 8080:5000 wallet-sim:latest
```

Run detached (background):

```bash
docker run -d --name Currency-Wallet-Sim -p 8080:5000 wallet-sim:latest
```

Open the UI at:

- `http://127.0.0.1:8080/`

Open the API at:

- `http://127.0.0.1:8080/api/wallets`

Stop and remove (when running detached):

```bash
docker stop Currency-Wallet-Sim
docker rm Currency-Wallet-Sim
```

---

<a id="notes"></a>

## Notes

- The frontend is served by the Flask backend (no separate frontend server).
- Automated tests avoid calling the real external FX provider by stubbing `EXCHANGE_API_URL`.
- CI runs on Python 3.12; Docker uses Python 3.11.

---

<a id="author"></a>

## 👥 Author

- **Marcus R. Kjærsgaard**  
  [![GitHub](https://img.shields.io/badge/GitHub-marcus--rk-black?logo=github)](https://github.com/marcus-rk)
