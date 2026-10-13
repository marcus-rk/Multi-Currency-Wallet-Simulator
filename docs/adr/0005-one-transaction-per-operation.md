---
status: accepted
---

# One database transaction per operation

Each repository function committed on its own, so an exchange made three separate commits and a failure between them could leave one wallet debited and the other not credited, against SRS sections 3.3.5 and 5.2. The service layer now runs each operation inside one transaction, opened with `BEGIN IMMEDIATE` through a single context manager in `app/database.py` that commits on success and rolls back on any exception; repository functions never commit. Because the SRS also requires a rejected operation to leave a FAILED transaction, that record is written after the rollback, in its own short transaction.

## Considered options

- **Commit in the repositories (the old design).** Simple, but not atomic.
- **Plain `BEGIN` (deferred).** Atomic, but two concurrent operations could both read the same balance before either writes, and one update would be lost.

## Consequences

- `BEGIN IMMEDIATE` takes SQLite's write lock before the balance is read, so concurrent operations run one after another and no update is lost. This is explained here rather than proven by a thread-based test, which on SQLite tends to be timing-dependent and flaky.
- A failure-injection test makes the transaction-record write fail mid-operation and asserts that no balance changed and exactly one FAILED transaction exists.
- Opening transactions in one place keeps a later database change (ADR-0001) contained to `app/database.py` and the repositories.
