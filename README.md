[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Embedded%20DB-lightgrey.svg)](https://www.sqlite.org/index.html)
[![Pytest](https://img.shields.io/badge/Pytest-Testing-orange.svg)](https://docs.pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-E2E%20Tests-purple.svg)](https://playwright.dev/)
[![JMeter](https://img.shields.io/badge/JMeter-Performance-red.svg)](https://jmeter.apache.org/)

# Multi-Currency Wallet Simulator

A small backend-focused project that simulates a single-user multi-currency wallet with deposits, withdrawals, exchanges, and transaction history exposed through a REST API and a minimal HTML/JS frontend.

The project is designed as a **testing playground**: unit, integration, API, E2E (Playwright) and performance (JMeter) tests are first-class citizens, not an afterthought.

---

## Domain Concepts & Project Elements

This project is focused on making a small **multi-currency wallet simulator** for:

- **Managing wallets** – create wallets in different currencies and see their balances.
- **Moving money** – make deposits, withdrawals and currency exchanges between wallets.
- **Seeing history** – view a simple log of what happened to a wallet over time.
- **Using external API** – fetches live (?or stubbed in tests?) exchange rates to support currency conversions.

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
- `.env`, `.flaskenv` – local environment and Flask configuration
- `requirements.txt` – Python dependencies
- `README.md` – main project documentation (this file)

---

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install --upgrade pip
```

---

## 👥 Author

- **Marcus R. Kjærsgaard**  
  [![GitHub](https://img.shields.io/badge/GitHub-marcus--rk-black?logo=github)](https://github.com/marcus-rk)

---

... More to come