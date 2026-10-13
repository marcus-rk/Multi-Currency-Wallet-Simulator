# Agent instructions

This file is the single source of instructions for any coding agent working in this repository. `CLAUDE.md` imports it; do not copy its content elsewhere.

## Before doing anything

1. Read [README.md](README.md) and the parts of `docs/` that touch the area you are working in.
2. Understand the existing project before proposing changes: its purpose, structure, tests and the decisions it already made. Start from what the code does now.
3. Before writing code, read [docs/agents/coding-standards.md](docs/agents/coding-standards.md). Before writing tests, read [ADR-0002](docs/adr/0002-classical-test-style.md) and [tests/testing_approach_wallet_simulator.md](tests/testing_approach_wallet_simulator.md).

## Checks

CI runs these three checks. Run them before saying a change works, and show their output:

```bash
python -m pylint app --fail-under=8.0
python -m pytest tests/unit --cov=app --cov-report=term-missing
python -m pytest -m integration
```

CI also runs SonarCloud, which cannot run locally.

## Separate facts, suggestions and decisions

When reporting or proposing, label each point:

- **Fact:** observed in code, command output or Git history. Cite the file, line or command.
- **Suggestion:** your recommendation or an option. Say why and what it costs.
- **Decision:** agreed with the owner. Only the owner makes these; note where and when it was agreed.

Never present a suggestion as if it were decided.

## Scope

- Discuss intended outcomes and scope with the owner before any rework.
- Do not change application code, upgrade dependencies, refactor, or add features unless that specific work has been agreed.
- Keep agreed changes small, and keep the project's original strengths intact.
- The owner must be able to explain every change. Prefer changes they can understand and defend over clever ones.

## Git workflow

- Start from the latest `origin/main` (`git pull --ff-only`).
- Work on a branch, never directly on `main`. Open pull requests as drafts; mark them ready only when the owner asks.
- Commit and push only when the owner asks.
- Use the GitHub account `marcus-rk`. The commit name and email (GitHub noreply address) are set in the local Git config; do not change it or the global config.
- Write all commits, pull requests and documentation in English.

## Agent skills

### Issue tracker

GitHub Issues in `marcus-rk/Multi-Currency-Wallet-Simulator`, via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: this repo has one `CONTEXT.md` and `docs/adr/` at its root. See `docs/agents/domain.md`.
