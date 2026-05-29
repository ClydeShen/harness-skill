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

Sizing convention:

| Field | Type | Unit | Mapping |
|---|---|---|---|
| **Effort (windows)** | number | Token budget | 1 = ~150K–200K tokens (single slice); 2 = ~300K–400K (1 phase); 3 = ~500K–700K (full feature); 4+ = epic |
| **Size** | T-shirt | Rough relative | XS ≤ 1 window; S = 2; M = 3–4; L = 5–6; XL ≥ 7 |
| **Priority** | single-select | Urgency tier | P1 = critical/blocking; P2 = normal; P3 = low/nice-to-have |

All three fields are created and populated automatically by harness skills: `setup-harness-skills` creates them on the board and writes their IDs to `.claude/harness.json`; `harness-triage` and `harness-issues` set the values per issue.

Effort is read by `context-handover` for session budget planning. Set from the `Effort:` field in an agent brief. Execute agent updates if actual effort differs significantly. See [effort calibration](../harness-triage/references/effort-calibration.md).

## Human gates

1. **Needs Review → Ready for Agent:** Human validates AC sources and confidence declaration for HITL stories. This is the plan phase exit gate — no issue moves to execute until human approves.
2. **In Progress → Done:** Human merges the PR. Branch protection enforces this gate — direct pushes to main are blocked.

## Phase exit oracles

| Phase | Oracle |
|---|---|
| discuss | Discuss Phase Tracking Issue has label `discuss-approved` or is closed by human |
| plan | All `phase:execute` issues have `status:ready-for-agent` (none remain in `needs-review`) |
| execute | All `phase:execute` issues are closed via merged PRs |
| verify | All `phase:verify` issues are `status:done`; no open `priority:p1` bugs remain |
