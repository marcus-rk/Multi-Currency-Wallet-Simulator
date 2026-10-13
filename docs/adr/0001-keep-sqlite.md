---
status: accepted
---

# Keep SQLite as the database

The money-correctness fixes (exact storage and one transaction per operation) need a database that supports exact values and real transactions. SQLite does both: it is fully ACID and can store exact integers. We keep it rather than move to MySQL in Docker, because this project's strength is its testing: every integration test gets a fresh, isolated SQLite file through `tmp_path`, which keeps the suite fast and needs no database service in CI.

## Considered options

- **MySQL in Docker Compose**, with `DECIMAL` columns and `SELECT ... FOR UPDATE`. Rejected for now: a new driver, a Compose setup with a healthcheck, rewritten SQL and a database service in CI, none of which the defects require.

## Consequences

- Moving to another database stays a possible later extension. To keep that door open, all SQL stays in the repository layer, and transactions are opened in one place (see the transaction boundary ADR), so a move means replacing that layer rather than the services or domain.
- SQLite allows one writer at a time. That is acceptable for a single-user simulator.
