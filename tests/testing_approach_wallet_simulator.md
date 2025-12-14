# Testing Approach – Wallet Simulator

This document explains the testing strategy so future tools/agents understand what to generate and where to put things.

## High-level philosophy

- **Black-box design–driven tests**  
  All tests are derived from:
  - Equivalence Partitioning (EP)
  - 3-value Boundary Value Analysis (BVA)
  - Decision Tables (deposit / withdraw / exchange)
  - State Transition Diagram (wallet lifecycle)

- **Testing philosophy: Classical vs London**

  - We follow a **classical (Chicago, state-based) unit testing philosophy**:
    - A unit is a pure function or a small cluster of in-memory code.
    - We assert on **state and outputs**, not on interactions with mocks.
    - We only replace **external/unmanaged dependencies** (like the FX API) with stubs/mocks.
  - We **do not** follow a strict London/mockist style:
    - We do *not* mock every internal collaborator.
    - We prefer real in-memory code for internal dependencies and use mocks only where they add clear value.
    - External API can be slow and we want fast unit test for regression testing

  **Pros of this classical approach:**
  - Tests are realistic: they exercise real domain logic without a forest of mocks.
  - Tests are more robust to refactoring of internal implementation.
  - Easier to trace tests back to black-box design (inputs → outputs).

  **Trade-offs compared to London/mockist:**
  - Slightly less isolation: some bugs involving collaborators appear only in integration tests.
  - We mitigate this with a clear separation:
    - pure unit tests in `domain`,
    - integration/API tests for `service` + DB + FX stub.

---

## Code structure

```text
app/
  domain/
    models/   # dataclasses
    rules/    # pure business rules derived from black-box design
  services/ # orchestrates domain + repositories + external API
  repository/
    wallets_repo.py
    transactions_repo.py
  routes/  # Flask routes, calling service layer
  config.py
  database.py
  __init__.py
```

- `domain` = **business rules only**, no Flask, no DB, no HTTP, no external API.
- `services` = **orchestration layer** combining:
  - domain rules,
  - database repositories,
  - external FX client (in production) or stub/mock (in tests).
- `routes` = HTTP layer (Flask) that calls the service layer.
- `repository` + `database` = persistence setup and data access.

---

## Test types and where they live

### 1. Unit tests (focus: `app/domain`)

**Scope**

- Only test functions in `app/domain/rules` and simple behaviour on `app/domain/models`.
- No DB, no Flask, no external network.
- No external API clients at all.

**Philosophy**

- **Classical unit testing (state-based)**:
  - Isolated logic, no shared dependencies.
  - Deterministic, fast, heavily parametrised.
  - Assertions on *return values* and *state*, not on mocked interactions.
- **Black-box driven**:
  - Input values come from EP and BVA (Amount EP, Balance EP, Currency EP, `amount ≤ balance` boundary, wallet states).
  - Conditions and outcomes come from decision tables and state diagram.

**Conventions**

- AAA comments:
  - `# Arrange`
  - `# Act`
  - `# Assert`
- Positive / Negative / Data type sections:
  - e.g. `# Positive testing`, `# Negative testing`, `# Data type testing`
- `@pytest.mark.parametrize` to cover EP/BVA values.

---

### 2. Integration tests (focus: `app/services` + DB + FX stub/mock)

**Scope**

- Test service functions in `app/services/*` that:
  - load from DB via repositories,
  - call `domain.rules`,
  - save updated entities + transactions,
  - call an **external api**.

**What makes them integration tests**

- Use a **real SQLite test database** (often in-memory).
- Use **real repository implementations**.
- Use a **stub/mock API client** instead of the real external API.

The FX client is always mocked/stubbed in tests because it is an **external, unmanaged dependency**:
- we cannot control its uptime or responses,
- we want tests to be fast, deterministic, and runnable offline,
- we don’t want to hit rate limits or pay for external calls in CI.

**Pros of mocking/stubbing the external API**

- Deterministic: we can simulate success, failure, timeouts on demand.
- Fast: tests do not wait on network or third-party services.
- Reliable: CI does not fail because the external service is down.
- Isolated: we test *our* logic around FX usage, not the provider’s internals.

**Cons / trade-offs**

- We must be careful that our stub behaviour matches the real API contract.
- There is a risk of “false confidence” if the real API changes and tests still pass.
- To mitigate this, we can:
  - keep the FX client interface very small and well-documented,
  - optionally add a small number of manual/occasional “contract” checks against a real sandbox environment (outside automated unit/CI tests).

---

### 3. Internal API tests (focus: Flask routes + service + DB + FX stub/mock)

**Scope**

- Use Flask’s test client to hit the HTTP endpoints (`app/routes`).

**Classification**
- These are *also* integration tests, but at the HTTP level (“internal API tests”).
- The external FX client is still mocked/stubbed here, for the same reasons as above.

---

## How all this ties back to the Black-Box design

- EP & BVA tables → define **input partitions and boundary values**.  
  These are reused as parameters in unit tests.

- Decision Tables (Deposit, Withdraw, Exchange) → define **conditions and outcomes**.  
  These become:
  - branches and checks in `domain.rules`,
  - different case rows in parametrised tests.

- State Transition Diagram → defines **allowed state changes and forbidden ones**.  
  These become:
  - state-related helpers in `domain.rules` or on the dataclasses,
  - explicit tests for valid/invalid transitions.

---

## Summary for future agents/tools

- **Unit tests**:
  - target `app/domain`,
  - follow AAA,
  - one behaviour per test and good naming,
  - use parametrised values from Black-Box-Test-Design (EP/BVA/decision tables/state transitions),
  - never touch DB, Flask, or the external API.

- **Integration tests (service)**:
  - target `app/services` + real SQLite test DB + real repositories,
  - use **mocked/stubbed FX client** to simulate external API behaviour.

- **Internal API tests**:
  - target Flask routes + service + DB using Flask’s test client,
  - still use the same FX stub/mock instead of the real external API.

- **Test philosophy**:
  - black-box design–driven,
  - **classical (Chicago) unit testing** on the domain layer (state-based, no unnecessary mocks),
  - integration tests for DB and external interactions,
  - explicit, small, behaviour-focused tests with clear naming and AAA structure,
  - external (unmanaged) dependencies are always stubbed/mocked in automated tests for determinism, speed, and reliability.
