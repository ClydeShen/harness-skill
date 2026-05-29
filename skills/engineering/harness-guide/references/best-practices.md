# Harness Best Practices

Practices that constitute a well-aligned Compound Engineering harness. Used in Phase 2 — Classify to populate the ✅ Already aligned bucket.

Reference: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Stop Hook

**What:** A `Stop` entry in `.claude/settings.json` that fires before Claude declares a task complete.

**Why:** Without a stop gate, the agent can exit after planning or after partial implementation, declaring success based on Confidence Exit or Fuzzy Done. The stop hook forces a final verification prompt.

**Signal of alignment:** `.claude/settings.json` contains a `Stop` entry with a non-empty command.

---

## PostToolUse Hook

**What:** A `PostToolUse` entry in `.claude/settings.json` that fires after every file write or edit.

**Why:** Incremental verification catches regressions at the point of change, not at the end of a session. Cheaper to fix immediately than after five more writes have layered on top.

**Signal of alignment:** `.claude/settings.json` contains a `PostToolUse` entry matched to `Write` or similar.

---

## Instruction File Quality

**What:** `CLAUDE.md` or `AGENTS.md` present, under 200 lines, with key commands (dev server, lint, build, test) and project constraints.

**Why:** An absent or stale instruction file means the agent starts every session without context. A file over 200 lines is too long to reliably fit in working context and degrades with age.

**Signal of alignment:** Instruction file present, ≤200 lines, includes a command reference block.

---

## Memory System

**What:** A configured memory system — `MEMORY.md` (zero-dep file), [agentmemory](https://github.com/rohitg00/agentmemory) (coding-agent-native, `~/.agentmemory/`), or [mem0](https://mem0.ai) (general-purpose library).

**Why:** Without a memory system, interrupted session recovery requires git-log reconstruction or GitHub comments as the sole context source. Both are slow and incomplete.

**Signal of alignment:** `MEMORY.md` at project root, `~/.agentmemory/` present, `memory/` directory, or `mem0` in dependencies.

---

## CI Gates: Lint + Build

**What:** `.github/workflows/*.yml` runs both a lint step and a build step on every push.

**Why:** Build-only CI catches compile errors but not code quality issues. Lint catches style violations, unused imports, and type errors that the build would accept.

**Signal of alignment:** CI workflow contains both a lint command and a build command.

---

## Pre-Commit Hooks

**What:** `.pre-commit-config.yaml` or `.husky/` configured to run lint and/or type-check before commit.

**Why:** Pre-commit hooks catch violations at the earliest possible point — before they enter the repo. CI is the last line of defence; pre-commit is the first.

**Signal of alignment:** `.pre-commit-config.yaml` or `.husky/pre-commit` present and non-empty.

---

## Eval Coverage

**What:** Evals in `evals/promptfoo/` covering observable behavior — not just happy path, but failure modes and edge cases.

**Why:** Tests verify code structure; evals verify agent behavior. Without evals, skill regressions are invisible until a user reports unexpected output.

**Signal of alignment:** At least one `evals/promptfoo/<skill>.yaml` exists with both happy-path and failure-mode scenarios.

---

## Session Discipline

**What:** `.harness/state.json` tracking `session.status`, `position.active_task`, and phase. Three hooks (`SessionStart`, `Stop`, `PostToolUse`) maintain it automatically. One task active at a time.

**Why:** Without a session state machine, context handover is lossy, interruptions lose all progress, and task scope drifts across sessions.

**Signal of alignment:** `.harness/state.json` present with `session.status` and `position.active_task` fields. `.continue-here.json` present for active tasks.

---

## Init Script

**What:** `init.sh` at root that installs dependencies, sets up env vars, and verifies the environment is ready.

**Why:** Without a reproducible setup script, new sessions start from an unknown baseline. Dependency drift goes undetected.

**Signal of alignment:** `init.sh` at repo root, executable, with at least one install or setup command.

---

## One Active Task

**What:** Only one task in `status:in-progress` at a time. Other tasks are `status:ready-for-agent` or `status:done`.

**Why:** Multiple in-progress tasks lead to Context Drift, incomplete handoffs, and untested partial implementations.

**Signal of alignment:** GitHub Issues or `state.json → position.active_task` show exactly one active task per session.
