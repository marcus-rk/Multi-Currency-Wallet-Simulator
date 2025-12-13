# Postman API Tests

This folder contains the **Postman collection + environment** used for API-level testing of the backend (HTTP contract tests).

## What’s included
- `*.postman_collection.json` — requests + test scripts
- `*.postman_environment.json` — variables used by the collection (base URL, wallet IDs, amounts)
- `postman_run_49of49_passed.png` — evidence screenshot of a full 49 tests green run

## What these tests verify
- Each API endpoint returns the expected **HTTP status codes** and **JSON response shape**
- Positive and negative flows (e.g., valid deposit vs invalid amount, insufficient funds, not-found IDs)
- Stable invariants (balances change correctly, transactions are recorded, errors return `{ "error": ... }`)

## How to run
1. Start the backend (Docker) on port **8080**
2. Import the collection + environment into Postman
3. Select the environment (top-right in Postman)
4. Run the collection top-to-bottom using the Collection Runner

Base URL used by default:
- `http://localhost:8080`

## External FX usage (and why it’s not asserted everywhere)
The **exchange endpoint** may call the configured FX provider. In Postman we avoid asserting the exact numeric rate (it can vary), and instead assert stable outcomes (status codes, JSON contract, recorded transaction, balance invariants). Deterministic FX parsing and failure mapping are validated in automated unit/integration tests via stubs.

## Defects found during API testing
Negative tests revealed a backend crash on non-numeric `"amount"` input (returned **500 HTML**). This was fixed by treating invalid decimals as client input errors, returning **400 JSON** with `{ "error": "Invalid amount" }`. **These cases are now covered in both Postman and integration tests.**

## Testing philosophy note (classical vs London)
These Postman tests follow a **classical/black-box** approach: they treat the API as a boundary and verify observable behavior (contract + outcomes) rather than mocking internal collaborators. Mocking/stubbing is reserved for unit/white-box tests where we need deterministic control of internal branches (e.g., FX parsing edge cases).