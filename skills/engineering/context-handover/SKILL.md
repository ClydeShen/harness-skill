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

1. `.claude/session.json` → `current_phase` — use if present and non-null
2. Active GitHub issue labels → `phase:design / product / execution / testing`
3. Issue title/body keywords — "design"/"spec"/"ADR" → design; "PRD"/"story" → product; "implement"/"build"/"fix" → execution; "test"/"QA" → testing
4. Default to `execution` — note "phase inferred by default" in handoff doc

## Execution sequence

- [ ] **1. Invoke memory system** — call the active memory system's update mechanism (mem0, memobank, letta, or equivalent). It is a black box — trigger the update and move on. Budget: <5% of remaining context.

- [ ] **2. Write `.claude/handoff.md`** — overwrite in place (single unified file, no timestamps in path). See `phase-budgets.md` for what each phase's handoff focuses on. Rules:
  - Reference artifacts by path/URL only — never inline file contents
  - Include a "Suggested skills" section
  - Always include `Last updated: YYYY-MM-DD HH:mm` at the top
  - Budget: <5% of remaining context

- [ ] **3. Post GitHub handover comment** — only if `docs/agents/issue-tracker.md` exists AND active task has a GitHub issue number. Format:

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

- [ ] **4. Output to user:**
  - "Handover complete. Handoff doc: `.claude/handoff.md`."
  - "**Start your next session with `/session-start`.**"
  - "**To compact this session now, type `/compact`.**"

## Graceful degradation

| Missing | Action |
|---|---|
| No `docs/agents/` | Skip GitHub comment; still write handoff doc |
| No `session.json` | Use phase fallback chain above; create `session.json` from inferred values |
| No GitHub remote | Skip issue update; note "run /setup-harness-skills" |
| No memory system | Write key decisions inline in handoff doc under "Key decisions" |

See `phase-budgets.md` for per-phase handoff content and session budget tables.
