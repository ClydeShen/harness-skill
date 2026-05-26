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
5. `.planning/config.json` → prior GSD or harness setup? (read harness key if present)
6. `.planning/STATE.md` → prior session state?
7. `.planning/PROJECT.md` → prior project context?
8. `.claude/harness.json` → old config to migrate? (deprecated — migrate values to .planning/config.json)
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

## Section E — Session State Location

> "`.planning/STATE.md` tracks active phase, session status, and last-session context. This follows GSD's format — install GSD at any time and it reads this file directly. Confirm this path or override?"

## Output

After all five sections, show the draft of what will be written and confirm before writing. Then execute the 10-step output sequence in `output-steps.md` — it covers: `## Agent skills` block, `harness.json`, GitHub labels, milestones, Project v2 board, branch protection, CI scaffold, `.gitignore`, and seed files to `docs/agents/`.

### .planning/ files written by setup-harness-skills

1. `.planning/config.json` — GSD defaults + `harness` namespace (idempotent merge; never overwrites GSD keys)
2. `.planning/STATE.md` — from GSD state template (only if absent)
3. `.planning/PROJECT.md` — from GSD project template (only if absent)
4. `.planning/ROADMAP.md` — stub with four phase entries: 01-discuss, 02-plan, 03-execute, 04-verify (only if absent)

### .gitignore additions

```
.planning/phases/*/.continue-here.md   # handoff docs — ephemeral, never commit
```

### Migration (when old .claude/ artifacts exist)

- `.claude/harness.json` → merge values into `.planning/config.json` harness namespace
- `.claude/session.json` → copy Session Continuity values into `.planning/STATE.md`
- `.claude/handoff.md` → map into `.continue-here.md` XML sections (lossy — preserves content in `<context>`)
- Old files are NOT deleted — user confirms before removal

Print a setup summary at the end: ✅ completed · ⚠️ requires manual action · 📁 files written.

Then: "Run `/session-start` to begin your first session."
