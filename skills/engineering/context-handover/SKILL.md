---
name: context-handover
description: End-of-context-window session transition that saves memory, writes a handoff doc, posts a GitHub progress comment, and instructs the user to /compact for a clean next session. Use when context usage approaches 80%, when remaining tokens are insufficient for the current phase's remaining work, or when user says "handover", "context is full", "save progress", "end session". Distinct from /handoff (lightweight subagent briefing — no GitHub, no /compact).
argument-hint: "What will the next session focus on?"
---

# Context Handover

Saves session state so the next session can resume without information loss.

## State files

`.harness/state.json` — session lifecycle (read/write):
```json
{
  "version": "1.0",
  "session": { "status": "idle", "started_at": "ISO 8601", "last_session": "ISO 8601" },
  "position": { "phase": "01-discuss", "active_task": "...", "resume_file": "...", "stopped_at": "..." }
}
```

`.harness/phases/XX-name/.continue-here.json` — resume context (write):
```json
{
  "version": "1.0",
  "phase": "01-discuss",
  "task": 1,
  "total_tasks": 3,
  "status": "in_progress",
  "last_updated": "ISO 8601",
  "current_state": "...",
  "completed_work": ["..."],
  "remaining_work": ["..."],
  "decisions_made": ["..."],
  "blockers": [],
  "context": "...",
  "next_action": "..."
}
```

## When to trigger

- **Proactive:** After each tool call, check token usage. If ≥70% used and remaining tokens are insufficient to complete Review + Compound for the current phase — trigger immediately.
- **Safety net:** ≥80% total usage — if proactive trigger was missed.

Do NOT invoke `/compact` programmatically. Instruct the user to type it.

## Phase detection (priority order)

1. `.harness/state.json` → `position.phase` — use if present
2. Active GitHub issue labels → `phase:discuss / plan / execute / verify`
3. Issue title/body keywords — "design"/"spec"/"ADR" → discuss; "PRD"/"story" → plan; "implement"/"build"/"fix" → execute; "test"/"QA" → verify
4. Default to `execute` — note "phase inferred by default" in handoff doc

## Execution sequence

- [ ] **1. Invoke memory system** — check `.claude/settings.json` hooks first:
  - If the active memory system has a **Stop hook configured** (e.g. agentmemory's `stop.mjs`) — it fires automatically on session end, no action needed.
  - Otherwise — call the memory system's update mechanism (mem0, letta, or equivalent) manually. It is a black box — trigger the update and move on.
  - If no memory system is detected — write key decisions into the `decisions_made` array of `.continue-here.json` (fallback).
  - Budget: <5% of remaining context.

- [ ] **2. Write `.harness/state.json`** — atomic read → mutate → write:
  - Set `session.status: "idle"`
  - Set `session.last_session: <current ISO timestamp>`
  - Set `position.stopped_at: <one-line description of last action>`
  - Set `position.resume_file: <path to .continue-here.json>`
  - Budget: <1% of remaining context.

- [ ] **3. Write `.harness/phases/XX-name/.continue-here.json`** — derive XX-name from `position.phase`. Rules:
  - All string values: factual, no padding. `completed_work` and `remaining_work` are arrays of strings.
  - Reference artifacts by path only — never inline content.
  - `next_action`: one concrete sentence starting with a verb.
  - Budget: <5% of remaining context.

- [ ] **4. Post GitHub handover comment** — only if `docs/agents/issue-tracker.md` exists AND active task has a GitHub issue number. Format:

  ```
  ## Handover — YYYY-MM-DD HH:mm

  **Phase:** [current phase]
  **Session summary:** [1–3 sentences]
  **Next step:** [specific pick-up point]

  _[N] of ~[effort_estimate] context window(s) used so far (token budget: 1 = ~30–60K)._

  ---
  _🤖 Posted by `/context-handover` (AI-generated)_
  ```

- [ ] **5. Output to user:**
  - "Handover complete. Resume file: `.harness/phases/XX-name/.continue-here.json`."
  - "**Start your next session with `/session-start`.**"
  - "**To compact this session now, type `/compact`.**"

## Graceful degradation

| Missing | Action |
|---|---|
| No `.harness/` directory | Note "run /setup-harness-skills first"; skip state write |
| No `state.json` | Create it from inferred values; use phase fallback chain for `position.phase` |
| No `.continue-here.json` path resolvable | Write to `.harness/phases/XX-current/.continue-here.json` using `position.phase` |
| No `docs/agents/` | Skip GitHub comment; still write .continue-here.json |
| No GitHub remote | Skip issue update silently |
| No memory system | Write key decisions in `decisions_made` array of .continue-here.json |

See `phase-budgets.md` for per-phase handoff content and session budget tables.
