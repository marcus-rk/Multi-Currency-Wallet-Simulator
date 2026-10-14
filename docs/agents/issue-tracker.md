# Issue tracker and Project lifecycle

GitHub Issues in `marcus-rk/Multi-Currency-Wallet-Simulator` hold agreed scope and acceptance criteria. [Wallet — Portfolio](https://github.com/users/marcus-rk/projects/2) tracks delivery. Use `gh` from this repository; pass `-R marcus-rk/Multi-Currency-Wallet-Simulator` elsewhere.

## Before starting or changing work

1. Read the issue body, comments and newer owner decisions; inspect assignees, linked PRs, native parent/sub-issues and native dependencies. Check the actual blocker outcome: a closed blocker may have been cancelled rather than delivered. Parent/sub-issue links describe scope, not dependency order.
2. Verify Project membership and current Status, Area, Priority and triage labels. Inspect linked PR scope, draft state and actual closing relationships. Resolve conflicting evidence with the owner before dependent work.
3. Confirm explicit authorization for this task. Priority orders attention; Ready describes readiness; neither authorizes execution. Existing scope and generic skills do not expand the owner's authorization. Explicit task authorization can cover routine metadata maintenance within that scope; new scope, marking PRs ready and merging retain owner gates.
4. Record the accountable human and an execution claim before implementation: session identity, branch/worktree and PR when available. Assign `marcus-rk` only for confirmed active responsibility. A shared human assignee cannot distinguish concurrent agents: inspect existing claims and branches, coordinate overlap and keep one active executor per scope. Keep backlog unassigned unless responsibility is confirmed.

Only create issues for owner-agreed plan items. Verify each new agreed issue is in this Project and set Area, Priority and appropriate triage labels. Write in English. Suggestions remain proposals until agreed; public comments or other writes require authorization, which may already be provided by the current task.

## Project fields and status

Current Area options: `Overview`, `Money correctness`, `API consistency`, `Runtime and CI`, `Portfolio presentation`. Current Priority options: `High`, `Medium`, `Low`. Inspect live options before editing; ask the owner about new vocabulary rather than inventing values. Maintain fields and labels when agreed scope changes.

| Status | Meaning |
| --- | --- |
| Backlog | Awaiting specification, dependencies or owner decisions. |
| Ready | Specified and unblocked; execution still requires owner authorization. |
| In progress | Authorized active work, including a draft PR or an agreed parent with children underway. |
| In review | A non-draft PR after the owner explicitly asks to mark it ready. |
| Done | Accepted and delivered; code normally merged into the default branch and its issue closed. |

Status is separate from issue open/closed state and CI results. A draft is In progress even with passing CI. A review PR can still have failing CI. Closing an issue alone does not prove delivery. Record cancellation or replacement explicitly and reconcile its Project state without calling it delivered.

Open blockers normally keep work in Backlog. The owner may explicitly agree preparation when dependencies block merge but allow preparation to start; record the exception and its limits. Once authorized preparation starts, use In progress and preserve the blocker/merge gate. Recheck native dependencies rather than relying on stale body text.

## PR links, review and completion

Use `Closes #N` only when that PR fully resolves issue N. Use `Part of #N` or `Related to #N` for parent specifications and partial work. A child PR must not close its parent. Inspect GitHub's actual closing relationships after scope changes and before review or merge; body text alone is insufficient. Review agents check agreed scope, validation and closing links as well as code standards.

Open PRs as drafts; mark ready only when the owner asks. Merge and close/reopen issues only with owner authorization. After acceptance, verify delivery and issue state before setting Done. Reassess dependents and parents after completion or cancellation: confirm the blocker outcome satisfies their needs, then report eligibility without automatically promoting, starting or closing them.

After a pause, abandonment, replacement, scope change or reopening, reconcile Status, labels, claims, assignees and links against what remains active and delivered. Release or update stale execution claims so another session can safely take over.

## Commands and skill routing

- Read scope/comments: `gh issue view <n> --comments`; inspect PRs with `gh pr view <n> --comments` and `gh pr diff <n>`.
- Read native relations: `gh api repos/marcus-rk/Multi-Currency-Wallet-Simulator/issues/<n>/parent`, `/sub_issues`, `/dependencies/blocked_by` and `/dependencies/blocking`. If unavailable, record the limit and use explicit body links as a documented fallback.
- Inspect Project: `gh project field-list 2 --owner marcus-rk` and `gh project item-list 2 --owner marcus-rk`; verify membership and values after mutations.
- Create an agreed issue with `gh issue create --title "..." --body-file <file>`, then add it with `gh project item-add 2 --owner marcus-rk --url <issue-url>` and set fields.
- Use `gh issue edit <n>` for authorized labels/assignees and `gh issue comment <n> --body-file <file>` for authorized claims or findings. Use body files to preserve multiline text.
- Inspect closing links with GraphQL `PullRequest.closingIssuesReferences`; preserve nonclosing references for partial work.

When a skill says “publish to the issue tracker”, create only an owner-agreed issue. When it says “fetch the relevant ticket”, perform the preflight above. **PRs as a request surface: no.** Resolve a bare `#N` as issue or PR before acting.

Wayfinder maps use `wayfinder:map` and native sub-issues; child type labels are `wayfinder:<type>` when agreed. Native dependencies are canonical ordering, with numeric issue database IDs for edge creation. A frontier query finds candidates, not authorization: inspect scope, blockers and execution claims before claiming. A skill's resolve step does not grant permission to close an issue or its parent.
