---
name: session-start
description: Briefs the current session by reading session state, handoff doc, and memory to determine the active phase, task, and context budget. Outputs a structured briefing and detects whether the phase should be skipped or reverted based on observable artifacts. Use at the start of every long-running agent session, or when user says "start session", "what are we working on", "resume", "pick up where we left off", "what's the active task".
---

# Session Start

Explore → Evaluate → Brief. Never ask questions before reading available state.

## State file

Session state lives in `.harness/state.json`. Schema:

```json
{
  "version": "1.0",
  "session": {
    "status": "idle",
    "started_at": "ISO 8601",
    "last_session": "ISO 8601"
  },
  "position": {
    "phase": "01-discuss",
    "active_task": "task title string",
    "resume_file": ".harness/phases/01-discuss/.continue-here.json",
    "stopped_at": "brief description of last action"
  }
}
```

`session.status`: `"idle"` (clean close) | `"in_progress"` (active or interrupted).

## Execution sequence

- [ ] **1. EXPLORE** — if the `SessionStart` hook ran, state fields are already in your context window via `additionalContext` — use them directly. Otherwise read:
  - `.harness/state.json` → `session.status`, `session.last_active`, `position.*`
  - `.harness/config.json` → GitHub owner, repo, project board ID (harness key)
  - `.harness/phases/XX-name/.continue-here.json` → path from `position.resume_file`
  - `.git/config` → remote origin (fallback if config.json absent)
  - `CLAUDE.md` / `AGENTS.md` → `## Agent skills` block present? (setup indicator)
  - `.harness/phases/01-discuss/` → any `CONTEXT.md` files? (phase skip signal)
  - `.harness/phases/02-plan/` → any `PLAN.md` files? (phase skip signal)
  - `MEMORY.md` or top-3 memory entries relevant to active task
  - `.claude/handoff.md` → legacy fallback if .continue-here.json absent (deprecated)

  > **Note:** `session.status` and `session.started_at` are set automatically by the `SessionStart` hook before this skill runs. No manual state write needed.

- [ ] **2. RESUME CONTEXT** — determine if this is a clean resume or interrupted recovery:

  **Detect interrupted session:** if `session.status` is `"in_progress"` AND `session.last_active` is >5 minutes old → interrupted session. Output a **Recovery briefing** (see Step 5b).

  > If `last_active` is absent (hook not configured), fall back to: `session.started_at` >30 minutes old.

  **Clean resume chain (`session.status: "idle"` or absent):**
  - **a. `.harness/phases/XX/.continue-here.json`** — primary. Read `next_action`, `completed_work`, `remaining_work`.
  - **b. Memory system query** — query active memory system for entries relevant to the active task. No GitHub required. If roam MCP tools are available (`roam_context` or `roam_retrieve`), call `roam_retrieve <active_task>` and include the architecture snapshot in the briefing output.
  - **c. Mid-session recovery** (.continue-here.json stale or absent): `git log --oneline -20` + recent GitHub per-AC progress comments (`gh api repos/{owner}/{repo}/issues/{N}/comments --jq '[.[] | select(.body | startswith("Progress"))] | .[-5:]'`).
  - **d. Legacy `.claude/handoff.md`** — use only if .continue-here.json absent and no migration has run.
  - **e. Cold start** — nothing found.

- [ ] **3. EVALUATE** — apply phase skip/revert (observable checks only):

  | Condition | Action |
  |---|---|
  | `.harness/phases/01-discuss/` contains a `CONTEXT.md` | Skip discuss → set phase to plan |
  | `.harness/phases/02-plan/` contains a `PLAN.md` | Skip discuss + plan → set phase to execute |
  | `position.phase` is `02-plan` but no CONTEXT.md in `01-discuss/` | Revert to discuss |
  | `position.phase` is `03-execute` but no PLAN.md in `02-plan/` | Revert to plan |

  Log skip/revert in the briefing: *"Phase advanced to execute — found PLAN.md in 02-plan and approved CONTEXT.md."*

- [ ] **4. COLD-START** — if all of the above yield nothing (no config.json, state.json, .continue-here.json, GitHub issues):
  - Output: "No prior session state found."
  - Present what WAS found (e.g., "Found CLAUDE.md with no ## Agent skills block")
  - Suggest: "Run `/setup-harness-skills` to initialize .harness/ or describe what you'd like to work on."
  - Do NOT default to any phase. Wait for user input.

- [ ] **5. OUTPUT** — emit one of two briefing formats:

  **5a. Clean resume briefing:**
  ```
  ## Session briefing
  Phase: [discuss / plan / execute / verify] (0N-name)
  Active task: #N — [title]
  Effort remaining: ~N context window(s) (token budget: 1 = ~150K–200K tokens)
  Pick up from: [<next_action> from .continue-here.json]

  Budget for this session:
  [phase-specific table from context-handover/phase-budgets.md]

  Run /context-handover when approaching 80% usage.
  ```

  **5b. Recovery briefing (interrupted session detected):**
  ```
  ## Recovery briefing — interrupted session detected

  Last active: [session.last_active] — no context-handover was recorded.

  Phase: [position.phase]
  Active task: [position.active_task]
  Last known intent: [position.stopped_at, or next_action from stale .continue-here.json]

  ## What changed since interruption (git log)
  [output of: git log --after="<session.last_active>" --oneline]

  ## What to do
  Review the git log above. If work is partially complete, continue from the last commit.
  If the session left code in an inconsistent state, run lint+build before proceeding.

  Run /context-handover when approaching 80% usage.
  ```

Phase budget tables live in `../context-handover/phase-budgets.md`.
