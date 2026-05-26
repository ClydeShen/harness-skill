---
name: session-start
description: Briefs the current session by reading session state, handoff doc, and memory to determine the active phase, task, and context budget. Outputs a structured briefing and detects whether the phase should be skipped or reverted based on observable artifacts. Use at the start of every long-running agent session, or when user says "start session", "what are we working on", "resume", "pick up where we left off", "what's the active task".
---

# Session Start

Explore → Evaluate → Brief. Never ask questions before reading available state.

## Execution sequence

- [ ] **1. EXPLORE** — read project state before asking anything:
  - `.planning/STATE.md` → session_status, session_started, Current Position (phase, active task, status)
  - `.planning/STATE.md` → Session Continuity.Resume file → path to .continue-here.md
  - `.planning/config.json` → GitHub owner, repo, project board ID (harness key)
  - `.planning/phases/XX-name/.continue-here.md` → path from STATE.md Resume file
  - `.git/config` → remote origin (fallback if config.json absent)
  - `CLAUDE.md` / `AGENTS.md` → `## Agent skills` block present? (setup indicator)
  - `.planning/phases/01-discuss/` → any `CONTEXT.md` files? (phase skip signal)
  - `.planning/phases/02-plan/` → any `PLAN.md` files? (phase skip signal)
  - `MEMORY.md` or top-3 memory entries relevant to active task
  - `.claude/session.json` → legacy fallback if STATE.md absent (deprecated)
  - `.claude/handoff.md` → legacy fallback if .continue-here.md absent (deprecated)

- [ ] **2. WRITE SESSION STATE** — update STATE.md Session Continuity before reading prior state:
  - Set `session_status: in_progress`
  - Set `session_started: <current ISO timestamp>`
  - Set `Active task: #N — [title]` in Current Position (if known from prior state or user context)
  - Budget: <1% of remaining context

  This makes the state machine transition observable: context-handover sets `session_status: idle`; session-start sets `session_status: in_progress`. A session that is interrupted before context-handover fires leaves `in_progress` in place — detected by the next session-start reading a stale `session_started` timestamp.

- [ ] **3. RESUME CONTEXT** — determine if this is a clean resume or interrupted recovery:

  **Detect interrupted session:** if STATE.md `session_status` is `in_progress` AND `session_started` timestamp is >30 minutes old → this is an interrupted session. Output a **Recovery briefing** (see Step 6b).

  **Clean resume chain (session_status: idle or absent):**
  - **a. `.planning/phases/XX/.continue-here.md`** — primary. Read `<next_action>`, `<completed_work>`, `<remaining_work>`.
  - **b. Memory system query** — query active memory system for entries relevant to the active task. No GitHub required.
  - **c. Mid-session recovery** (.continue-here.md stale or absent): `git log --oneline -20` + recent GitHub per-AC progress comments (`gh api repos/{owner}/{repo}/issues/{N}/comments --jq '[.[] | select(.body | startswith("Progress"))] | .[-5:]'`).
  - **d. Legacy `.claude/handoff.md`** — use only if .continue-here.md absent and no migration has run.
  - **e. Cold start** — nothing found.

- [ ] **4. EVALUATE** — apply phase skip/revert (observable checks only):

  | Condition | Action |
  |---|---|
  | `.planning/phases/01-discuss/` contains a `CONTEXT.md` | Skip discuss → set phase to plan |
  | `.planning/phases/02-plan/` contains a `PLAN.md` | Skip discuss + plan → set phase to execute |
  | STATE.md `current_focus` is `02-plan` but no CONTEXT.md in `01-discuss/` | Revert to discuss |
  | STATE.md `current_focus` is `03-execute` but no PLAN.md in `02-plan/` | Revert to plan |

  Log skip/revert in the briefing: *"Phase advanced to execute — found PLAN.md in 02-plan and approved CONTEXT.md."*

- [ ] **5. COLD-START** — if all of the above yield nothing (no config.json, STATE.md, .continue-here.md, GitHub issues):
  - Output: "No prior session state found."
  - Present what WAS found (e.g., "Found CLAUDE.md with no ## Agent skills block")
  - Suggest: "Run `/setup-harness-skills` to initialize .planning/ or describe what you'd like to work on."
  - Do NOT default to any phase. Wait for user input.

- [ ] **6. OUTPUT** — emit one of two briefing formats:

  **6a. Clean resume briefing:**
  ```
  ## Session briefing
  Phase: [discuss / plan / execute / verify] (0N-name)
  Active task: #N — [title]
  Effort remaining: ~N context window(s)
  Pick up from: [<next_action> from .continue-here.md]

  Budget for this session:
  [phase-specific table from context-handover/phase-budgets.md]

  Run /context-handover when approaching 80% usage.
  ```

  **6b. Recovery briefing (interrupted session detected):**
  ```
  ## Recovery briefing — interrupted session detected

  Previous session started: [session_started timestamp] — no context-handover was recorded.

  Phase: [from STATE.md Current Position]
  Active task: #N — [title]
  Last known intent: [Stopped at from STATE.md, or <next_action> from stale .continue-here.md]

  ## What changed since interruption (git log)
  [output of: git log --after="<session_started>" --oneline]

  ## What to do
  Review the git log above. If work is partially complete, continue from the last commit.
  If the session left code in an inconsistent state, run lint+build before proceeding.

  Run /context-handover when approaching 80% usage.
  ```

Phase budget tables live in `../context-handover/phase-budgets.md`.
