# Coding Standards

How code in this repository is written and commented. These rules describe the conventions the existing code already follows; new code matches them. Test conventions live in [ADR-0002](../adr/0002-classical-test-style.md).

## Layers

Code is split into `app/domain` (pure rules, no database, Flask or network), `app/repository` (SQLite access), `app/services` (orchestration) and `app/routes` (HTTP).

- Only the repository layer runs SQL. Services and routes call repository functions.
- Domain rules stay pure: they take values and return new values.

Decided, being implemented (follow these in new code; the existing code does not yet):

- Only the repository layer converts between `Decimal` and integer minor units ([ADR-0004](../adr/0004-money-as-integer-minor-units.md), issue #4).
- Database transactions open in one place, in the database module ([ADR-0005](../adr/0005-one-transaction-per-operation.md), issue #8).

## Comments and docstrings

- Every module starts with a docstring of a few plain-text lines saying what the module is for and which layer it belongs to.
- Public functions get a short plain-text docstring (one to three lines). Do not add `Args:` or `Returns:` sections; type hints carry that information.
- Inline comments explain why, not what: a business rule, a decision, an SRS reference or a boundary to an external system. For example `# SRS v2.1: Round half up to 2 decimal places`.
- Do not comment code that reads clearly on its own.
- When a comment refers to a requirement or decision, name it (SRS section, ADR number).
- Section dividers (`# ----` blocks) are used only in test modules, to group test cases.

## Type hints

Annotate every function's parameters and return type, in all layers including tests.

## Lint

`.pylintrc` is the lint configuration. CI fails below a pylint score of 8.0; the code currently scores 10.00, and new code keeps it there.

- Fix a warning in the code rather than silencing it.
- If a warning must stay, disable it on that line only (`# pylint: disable=<check>`) with a comment saying why.
- Do not add checks to the `disable` list in `.pylintrc` or lower the CI threshold without the owner's agreement.

## Commits

Use Conventional Commits (`fix:`, `feat:`, `docs:`, `test:`, `refactor:`, `chore:`) in English. Put the reason for the change in the body and reference the issue (`Closes #4`).
