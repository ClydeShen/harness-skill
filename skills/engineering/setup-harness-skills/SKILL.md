---
name: setup-harness-skills
description: >
  Sets up an ## Agent skills block in AGENTS.md/CLAUDE.md and docs/agents/ so
  harness skills know the issue tracker, triage labels, domain docs, GitHub
  Project board, and session state location. Run before first use of triage,
  to-prd, to-issues, context-handover, or session-start — or if those skills
  appear to be missing context. Typically consumes <30% of a context window.
disable-model-invocation: true
---

# Setup Harness Skills

One-time gateway. **Explore first**, then ask questions one section at a time. Never dump all questions at once.

## Step 1 — Explore

Before asking anything, read and report a **one-line summary**:

1. `.git/config` → remote origin (owner/repo)
2. `CLAUDE.md` / `AGENTS.md` → existing `## Agent skills` block?
3. `CONTEXT.md` → present?
4. `docs/agents/` → prior setup files?
5. `.harness/config.json` → prior GSD or harness setup? (read harness key if present)
6. `.harness/state.json` → prior session state?
7. `.harness/PROJECT.md` → prior project context?
8. `.claude/harness.json` → old config to migrate? (deprecated — migrate values to .harness/config.json)
9. `~/.claude/skills/` → any `gsd-*` skill present? Any of `brainstorming`, `systematic-debugging`, `writing-plans`, `subagent-driven-development` present?

Example: "Found CLAUDE.md with no Agent skills block, no docs/agents/, GitHub remote owner/repo."

Append to the summary line if collections are missing:
- Both absent: `"Tip: GSD Redux and Superpowers are recommended companion collections — see https://github.com/open-gsd/get-shit-done-redux and https://github.com/obra/superpowers"`
- Only GSD Redux absent: `"Tip: GSD Redux not installed — https://github.com/open-gsd/get-shit-done-redux"`
- Only Superpowers absent: `"Tip: Superpowers not installed — https://github.com/obra/superpowers"`
- Both present: omit entirely.

## Section A — Issue Tracker

> "Where do issues live? Skills like `triage`, `to-prd`, and `to-issues` read from and write to it."

1. GitHub Issues — standard `gh issue` CLI commands
2. GitHub Projects v2 — GraphQL API board with custom fields
3. Local markdown — files in `.scratch/<feature>/`
4. Other — describe in prose

Wait for answer before Section B.

## Section A.5 — Instruction File

**Run only if neither CLAUDE.md nor AGENTS.md exists.**

> "No instruction file found. Which would you like to create?"
> 1. `CLAUDE.md` — standard for Claude Code projects
> 2. `AGENTS.md` — use when targeting multiple AI agents (Codex, Kiro, Gemini, etc.)

Do NOT choose unilaterally. Wait for the user's answer.

## Section B — Triage Labels

> "Five canonical labels: `status:needs-triage`, `status:needs-info`, `status:ready-for-agent`, `status:ready-for-human`, `status:wontfix`. Also: `status:needs-prd`, `status:needs-review`, `status:in-progress`, `status:done`. Use these or override?"

## Section C — Domain Docs

> "Single-context (one CONTEXT.md + docs/adr/) or multi-context (CONTEXT-MAP.md for monorepos)?"

Options: Single-context · Multi-context · Neither yet

## Section D — GitHub Project Board + Milestones

> "Which board should `context-handover` and `session-start` use? (Leave blank to skip.) Default columns: Triage → Needs PRD → Needs Review → Ready for Agent → In Progress → Done. Default milestones: Design, MVP, v1.0."

After confirming the board, inform the user of the two sizing fields (no new questions — informational only):

> "The board uses two sizing fields:
> - **Effort (windows):** token budget estimate — set from the `Effort:` value in an agent brief. 1 ≈ 30K–60K tokens (single slice); 2 ≈ 80K–150K (1 phase); 3 ≈ 200K–300K (full feature); 4+ = epic.
> - **Size** (T-shirt): rough relative size. Suggested mapping: XS ≤ 1 window, S = 2, M = 3–4, L = 5–6, XL ≥ 7.
> Both are optional but Effort is read by `context-handover` for session budget planning."

## Section E — Session State Location

> "`.harness/state.json` tracks active phase, session status, and last-session context as machine-readable JSON. Three hooks (`SessionStart`, `Stop`, `PostToolUse`) maintain it automatically. Confirm this path or override?"

## Section F — Context Window & Model

> "Which model are you using? This determines the context window size and affects session budget calculations."

1. **Claude Code** (Claude Sonnet 4) — 1M context (1,000,000 tokens) ✅ default
2. **Claude Code** (Claude Sonnet 3.5) — 200K context (200,000 tokens)
3. **Claude Code** (Claude Haiku 3.5) — 200K context (200,000 tokens)
4. **Custom model** — specify model name + context window in tokens

Wait for answer before proceeding.

If custom: ask for model name (e.g. `qwen2.5-coder-32b`) and context window size in tokens.

## Output

After all five sections, show the draft of what will be written and confirm before writing. Then execute the 10-step output sequence in `output-steps.md` — it covers: `## Agent skills` block, `harness.json`, GitHub labels, milestones, Project v2 board, branch protection, CI scaffold, `.gitignore`, and seed files to `docs/agents/`.

### .harness/ files written by setup-harness-skills

1. `.harness/config.json` — GSD defaults + `harness` namespace (idempotent merge; never overwrites GSD keys)
2. `.harness/state.json` — session state JSON (only if absent; see `session-config.md` for schema)
3. `.harness/PROJECT.md` — from GSD project template (only if absent)
4. `.harness/ROADMAP.md` — stub with four phase entries: 01-discuss, 02-plan, 03-execute, 04-verify (only if absent)
5. `.harness/settings.json` — model type + context window size (always written; idempotent merge)

### .gitignore additions

```
.harness/phases/*/.continue-here.json   # resume context — ephemeral, never commit
```

### Migration (when old .claude/ artifacts exist)

- `.claude/harness.json` → merge values into `.harness/config.json` harness namespace
- `.claude/session.json` → extract phase/task values into `.harness/state.json` position fields
- `.harness/STATE.md` → extract session fields into `.harness/state.json` (then delete STATE.md)
- `.claude/handoff.md` → map into `.continue-here.json` fields (lossy — preserves content in `context`)
- Old files are NOT deleted — user confirms before removal

Print a setup summary at the end: ✅ completed · ⚠️ requires manual action · 📁 files written.

Then: "Run `/session-start` to begin your first session."
