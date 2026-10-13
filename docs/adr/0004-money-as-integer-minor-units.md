---
status: accepted
---

# Store money as integer minor units

Balances and transaction amounts were declared `NUMERIC`, which SQLite stores as a binary float, so `0.10 + 0.20` did not round-trip exactly, although the domain and the API already work in `Decimal` and decimal strings. Every amount is now stored as an `INTEGER` count of its currency's minor unit (for example 1050 for 10.50 DKK). Each `Currency` declares its number of decimal places, and conversion between `Decimal` and minor units happens only in the repository layer, so the domain, services and API are unchanged. This is the convention payment APIs such as Stripe and Adyen use, and it works on databases without an exact decimal type.

## Considered options

- **TEXT holding the decimal string.** Exact, but SQL cannot sum, compare or `CHECK` it.
- **Keep `NUMERIC`.** This was the defect.
- **`DECIMAL` columns.** The natural choice on MySQL or PostgreSQL, but SQLite has no exact decimal type (see ADR-0001).

## Consequences

- An amount with more decimals than its currency allows cannot be stored, so requests with such amounts are rejected (see `docs/srs-addendum.md`).
- Exact SQL sums and constraints such as `CHECK (balance >= 0)` become possible.
- Existing database files must be recreated. No persistent data exists: the database is created on start and the seed script resets it.
- SQLite integers are 64-bit, far above the maximum amount per operation.
