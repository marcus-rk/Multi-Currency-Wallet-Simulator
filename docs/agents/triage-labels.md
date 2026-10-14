# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repository's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Specified and suitable for agent work  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Check live labels with `gh label list`; ask the owner before creating new vocabulary. Maintain labels alongside Project fields using the lifecycle in [issue-tracker.md](issue-tracker.md).

`ready-for-agent` describes specification quality and agent suitability. It does not override blockers, Project Status or owner authorization. It can remain on a specified blocked issue in Backlog. `ready-for-human` identifies work requiring human action; it does not assign or authorize that action.
