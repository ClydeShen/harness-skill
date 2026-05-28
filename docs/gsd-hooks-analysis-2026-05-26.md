# GSD Hooks Analysis — 2026-05-26

Research into gsd-build/get-shit-done hooks and open-gsd/get-shit-done-redux concepts
and their applicability to this project.

---

## Hooks Studied

From `gsd-build/get-shit-done/tree/main/hooks`:

| File | Type | Purpose |
|---|---|---|
| gsd-statusline.js | UserDefinedStatusBar | Context bar + active task for user; writes metrics bridge to `/tmp` |
| gsd-context-monitor.js | PostToolUse | Reads bridge file, injects agent-facing warnings at 35%/25% remaining |
| gsd-session-state.sh | SessionStart | Injects STATE.md head as additionalContext at every session open |
| gsd-workflow-guard.js | (not fetched) | Guards tool call sequences |
| gsd-prompt-guard.js | (not fetched) | Intercepts prompt injection attempts |
| gsd-read-guard.js | (not fetched) | Guards file read operations |

---

## Fit Assessment vs. Current Skills

### Already covered — don't borrow

| GSD concept | Current equivalent |
|---|---|
| Session state injection at start | `session-start` + `context-handover/phase-budgets.md` |
| Handoff doc on context exhaustion | `context-handover` (writes `.claude/handoff.md`) |
| Phase lifecycle (design → product → execution → testing) | `context-handover` + `session-start` phase chain |
| Issue breakdown with HITL/AFK routing | `to-issues` |
| PRD generation from context | `to-prd` |

### Genuinely new value — worth adding to harness-engineering

**1. `gsd-context-monitor.js` — agent-facing context warnings (PostToolUse)**

The current skill recommends a Stop hook and a PostToolUse Write hook, but says nothing
about a context-pressure hook. GSD's monitor injects `additionalContext` warnings directly
into the agent's conversation when remaining tokens drop below 35% (WARNING) and 25%
(CRITICAL). The agent sees the warning and can act before context is exhausted.

Key design details:
- Reads metrics from `/tmp/claude-ctx-{session_id}.json` written by the statusline hook
- Debounces: 5 tool uses minimum between warnings
- Severity escalation (WARNING → CRITICAL) bypasses debounce
- On CRITICAL + GSD active: auto-records session state as a resume breadcrumb
- Never uses imperative commands that override user preferences
- Graceful: exits silently if no metrics file (subagent / fresh session)

**Gap:** harness-engineering currently has no detection for missing context-monitor hook.
This is a real harness gap the skill should surface.

**2. `gsd-session-state.sh` — SessionStart hook**

GSD uses the `SessionStart` hook event to inject project state (phase, config mode)
as `additionalContext` so the agent orients itself without being asked. The hook is
opt-in (`hooks.community: true` in config.json) and outputs structured JSON with
typed fields (`state_present`, `config_mode`) alongside the prose.

**Gap:** harness-engineering currently only detects Stop and PostToolUse hooks.
SessionStart is a third hook type worth surfacing as an optional recommendation.

### Concepts that don't apply

- **Full 6-command GSD workflow** (`/gsd-new-project` → `/gsd-execute-phase` → `/gsd-ship`):
  Competing orchestration system; importing wholesale would replace current skills.
- **`.harness/` artifact structure** (`STATE.md`, `REQUIREMENTS.md`, `ROADMAP.md`):
  GSD-specific; conflicts with current `.claude/session.json` + `docs/agents/` approach.
  Mixing both would confuse users.
- **36 specialised subagents**: GSD-specific parallelisation architecture; out of scope
  for a skill collection designed for simpler Claude Code use.
- **Phase lifecycle management**: Already covered by context-handover + session-start.

---

## GSD-Redux Assessment

Repo: `open-gsd/get-shit-done-redux` (`@opengsd/get-shit-done-redux`)

Same hook inventory as gsd-build (statusline, context-monitor, session-state, etc.)
plus additional hooks not yet fetched: gsd-workflow-guard.js, gsd-prompt-guard.js,
gsd-read-guard.js, gsd-read-injection-scanner.js.

These guard hooks (workflow-guard, prompt-guard, read-guard) are defensive patterns
that go beyond anything in the current skill set. Worth inspecting before deciding
whether a dedicated `install-hooks` skill is warranted.

---

## Recommended Actions

**Narrow (update harness-engineering only):**
- Add detection of missing SessionStart hook (optional recommendation)
- Add detection of missing context-monitor PostToolUse hook
- Add paste-ready snippets for both in `universal-snippets.md`

**Broader (if guard hooks are useful after inspection):**
- Fetch gsd-workflow-guard.js, gsd-prompt-guard.js, gsd-read-guard.js
- Decide whether a new `install-hooks` skill is warranted alongside updating harness-engineering
