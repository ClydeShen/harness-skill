---
name: context-handover
description: End-of-context-window session transition that saves memory, writes a handoff doc, posts a GitHub progress comment, and instructs the user to /compact for a clean next session. Use when context usage approaches 80%, when remaining tokens are insufficient for the current phase's remaining work, or when user says "handover", "context is full", "save progress", "end session". Distinct from /handoff (lightweight subagent briefing — no GitHub, no /compact).
argument-hint: "What will the next session focus on?"
---

# Context Handover

Saves session state so the next session can resume without information loss.

## When to trigger

- **Proactive:** After each tool call, check token usage. If ≥70% used and remaining tokens are insufficient to complete Review + Compound for the current phase — trigger immediately.
- **Safety net:** ≥80% total usage — if proactive trigger was missed.

Do NOT invoke `/compact` programmatically. Instruct the user to type it.

## Phase detection (priority order)

1. `.planning/STATE.md` → `Current Position.Phase` field — use if present
2. `.claude/session.json` → `current_phase` — legacy fallback (deprecated)
3. Active GitHub issue labels → `phase:discuss / plan / execute / verify`
4. Issue title/body keywords — "design"/"spec"/"ADR" → discuss; "PRD"/"story" → plan; "implement"/"build"/"fix" → execute; "test"/"QA" → verify
5. Default to `execute` — note "phase inferred by default" in handoff doc

## Execution sequence

- [ ] **1. Invoke memory system** — call the active memory system's update mechanism (mem0, memobank, letta, or equivalent). It is a black box — trigger the update and move on. Budget: <5% of remaining context.

- [ ] **2. Update `.planning/STATE.md` Session Continuity** — write `session_status: idle`, `last_session`, `Stopped at`, `Resume file` fields. Budget: <1% of remaining context.

- [ ] **3. Write `.planning/phases/XX-name/.continue-here.md`** — use GSD's exact template. Path: derive XX-name from STATE.md `Current Position.Phase`. Rules:
  - YAML frontmatter: phase, task, total_tasks, status, last_updated
  - XML sections: current_state, completed_work, remaining_work, decisions_made, blockers, context, next_action
  - Reference artifacts by path only — never inline content
  - Budget: <5% of remaining context

  Template:
  ```
  ---
  phase: 03-execute
  task: 2
  total_tasks: 5
  status: in_progress
  last_updated: YYYY-MM-DDTHH:MM:SSZ
  ---

  <current_state>
  Where exactly are we?
  </current_state>

  <completed_work>
  - Task 1: [name] — Done
  </completed_work>

  <remaining_work>
  - Task 2: [what's left]
  </remaining_work>

  <decisions_made>
  - Decided to use X because Y
  </decisions_made>

  <blockers>
  None
  </blockers>

  <context>
  Mental state and vibe to resume smoothly.
  </context>

  <next_action>
  Start with: [specific action]
  </next_action>
  ```

- [ ] **4. Post GitHub handover comment** — only if `docs/agents/issue-tracker.md` exists AND active task has a GitHub issue number. Format:

  ```
  ## Handover — YYYY-MM-DD HH:mm

  **Phase:** [current phase]
  **Session summary:** [1–3 sentences]
  **Next step:** [specific pick-up point]
  **Handoff doc:** `.claude/handoff.md`

  _[N] of ~[effort_estimate] context window(s) used so far._

  ---
  _🤖 Posted by `/context-handover` (AI-generated)_
  ```

  Also update `session.json`: set `last_handover` and `next_session_hint`.

- [ ] **5. Output to user:**
  - "Handover complete. Resume file: `.planning/phases/XX-name/.continue-here.md`."
  - "**Start your next session with `/session-start`.**"
  - "**To compact this session now, type `/compact`.**"

## Graceful degradation

| Missing | Action |
|---|---|
| No `.planning/` directory | Note "run /setup-harness-skills first"; write `.claude/handoff.md` as emergency fallback only |
| No `.continue-here.md` path resolvable | Write to `.planning/phases/XX-current/.continue-here.md` using STATE.md `current_focus` value |
| No `docs/agents/` | Skip GitHub comment; still write .continue-here.md |
| No `session.json` or STATE.md | Use phase fallback chain; create STATE.md from inferred values |
| No GitHub remote | Skip issue update silently |
| No memory system | Write key decisions inline in `<decisions_made>` section of .continue-here.md |

See `phase-budgets.md` for per-phase handoff content and session budget tables.
