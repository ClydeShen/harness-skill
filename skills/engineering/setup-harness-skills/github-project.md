# GitHub Project Board

**Board ID:** [written by /setup-harness-skills from harness.json — do not edit manually]
**Board name:** [written by /setup-harness-skills]

## Columns

| Column | Status label | Who moves here | Human action? |
|---|---|---|---|
| Triage | `status:triage` | Agent | No |
| Needs PRD | `status:needs-prd` | Agent | No |
| Needs Review | `status:needs-review` | Agent (HITL stories) | **Yes — human validates AC + sources** |
| Ready for Agent | `status:ready-for-agent` | Human (from Needs Review) or Agent (AFK) | Triggers execution |
| In Progress | `status:in-progress` | Agent (`/session-start`) | No |
| Done | `status:done` | GitHub (PR merged) | **Yes — human merges PR** |

## Custom fields

- **Effort (windows):** number field — Product-phase agent's estimate of context windows to complete the issue. Execution agent updates if actual effort differs significantly.

## Human gates

1. **Needs Review → Ready for Agent:** Human validates AC sources and confidence declaration for HITL stories. This is the Product phase exit gate — no issue moves to execution until human approves.
2. **In Progress → Done:** Human merges the PR. Branch protection enforces this gate — direct pushes to main are blocked.

## Phase exit oracles

| Phase | Oracle |
|---|---|
| Design | Design Phase Tracking Issue has label `design-approved` or is closed by human |
| Product | All `phase:execution` issues have `status:ready-for-agent` (none remain in `needs-review`) |
| Execution | All `phase:execution` issues are closed via merged PRs |
| Testing | All `phase:testing` issues are `status:done`; no open `priority:p1` bugs remain |
