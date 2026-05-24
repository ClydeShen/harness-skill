---
name: session-start
description: Briefs the current session by reading session state, handoff doc, and memory to determine the active phase, task, and context budget. Outputs a structured briefing and detects whether the phase should be skipped or reverted based on observable artifacts. Use at the start of every long-running agent session, or when user says "start session", "what are we working on", "resume", "pick up where we left off", "what's the active task".
---

# Session Start

Explore → Evaluate → Brief. Never ask questions before reading available state.

## Execution sequence

- [ ] **1. EXPLORE** — read project state before asking anything:
  - `.claude/harness.json` → GitHub owner, repo, project board ID
  - `.claude/session.json` → phase, active task, effort estimate
  - `.claude/handoff.md` → last handover content
  - `.git/config` → remote origin (fallback if harness.json absent)
  - `CLAUDE.md` / `AGENTS.md` → `## Agent skills` block present? (setup indicator)
  - `docs/superpowers/specs/` → any `.md` files? (phase skip signal)
  - `MEMORY.md` or top-3 memory entries relevant to active task

- [ ] **2. RESUME CONTEXT** — four-tier recovery chain (use first that applies):
  - **a. `.claude/handoff.md`** — primary. Use if present.
  - **b. Mid-session recovery** (handoff.md stale or absent): read `git log --oneline -20` + fetch recent progress comments (`gh api repos/{owner}/{repo}/issues/{N}/comments --jq '[.[] | select(.body | startswith("Progress"))] | .[-5:]'`). Together these reconstruct what was completed without human intervention.
  - **c. Last GitHub handover comment** — only if handoff.md is absent AND one of: project re-cloned, active_task in session.json mismatches current in-progress issue, or user explicitly requests GitHub sync. Command: `gh api repos/{owner}/{repo}/issues/{N}/comments --jq '.[-1]'`
  - **d. Full comment history** — NEVER loaded automatically. Only if user explicitly requests.

- [ ] **3. EVALUATE** — apply phase skip/revert (observable checks only):

  | Condition | Action |
  |---|---|
  | ≥1 `.md` in `docs/superpowers/specs/` | Skip Design → set phase to Product |
  | `phase:execution` issues with `status:ready-for-agent` exist (and spec exists) | Skip Design + Product → set phase to Execution |
  | No `.md` in `docs/superpowers/specs/` | Revert to Design |
  | `current_phase == "product"` but no `phase:design` issue is closed or labelled `design-approved` | Revert to Design |
  | `current_phase == "execution"` but `gh issue list --label "phase:execution,status:ready-for-agent"` returns 0 | Revert to Product |

  Log skip/revert in the briefing: *"Phase advanced to Execution — found 3 ready-for-agent issues and an approved spec."*

- [ ] **4. INFER** — if `session.json` absent after evaluation: infer phase from GitHub issue labels.

- [ ] **5. COLD-START** — if all of the above yield nothing (no harness.json, session.json, handoff.md, GitHub issues, spec files):
  - Output: "No prior session state found."
  - Present what WAS found (e.g., "Found CLAUDE.md with no ## Agent skills block")
  - Suggest: "Run `/setup-harness-skills` to configure the harness, then describe what you'd like to work on."
  - Do NOT default to any phase. Wait for user input.

- [ ] **6. OUTPUT** — structured briefing:

  ```
  ## Session briefing
  Phase: [Design / Product / Execution / Testing]
  Active task: #N — [title]
  Effort remaining: ~N context window(s)
  Pick up from: [specific next step from handoff doc]

  Budget for this session:
  [phase-specific table from context-handover/phase-budgets.md]

  Run /context-handover when approaching 80% usage.
  ```

Phase budget tables live in `../context-handover/phase-budgets.md`.
