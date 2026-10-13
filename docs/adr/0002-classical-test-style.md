---
status: accepted
---

# New tests follow the classical (state-based) style

`tests/testing_approach_wallet_simulator.md` describes a classical style where only external dependencies are faked, but the original service white-box tests mock the repositories and rules. New tests follow the documented classical style: domain tests use no database, Flask or network; service, repository and API tests run against a real temporary SQLite database; only the exchange rate API is stubbed. The original tests stay as written, as evidence of the exam's testing techniques, and are changed only where a behaviour change forces it or a refactor clearly improves them.

## Conventions for new tests

- Name tests `test_<behaviour>_<outcome>`, for example `test_deposit_valid_amount_passes`.
- Mark each phase with a comment that says what it does: `# Arrange: ACTIVE wallet with 100.00 DKK`, `# Act: ...`, `# Assert: ...`.
- Name the technique in the module docstring (equivalence partitioning, boundary value analysis, decision table, state transition) and use `pytest.mark.parametrize` with a comment on each boundary case.
- Reuse the shared fixtures (`wallet_factory`, `get_fixed_timestamp`, `app_instance`, `client`, `fx_rate_stub`). A new fixture gets a docstring that starts with `WHY:`.
- Mark integration tests with `@pytest.mark.integration`.
- One behaviour per test.
