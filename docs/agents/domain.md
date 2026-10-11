# Domain Docs

How the engineering skills should consume this repository's domain documentation when exploring its codebase.

This is a single-context repository. Paths below are relative to the repository root.

## Before exploring, read these

- **`CONTEXT.md`** at the repository root, or
- **`CONTEXT-MAP.md`** at the repository root if it exists: it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

Creating `CONTEXT.md` or an ADR changes the repository. Get the owner's go-ahead and work on a branch, per the Git workflow in `AGENTS.md`.

## File structure

Single-context repository:

```
Multi-Currency-Wallet-Simulator/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-first-decision.md
│   └── 0002-second-decision.md
└── ...
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
