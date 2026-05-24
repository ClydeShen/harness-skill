---
name: harness-engineering
description: Scans a project for agent-harness gaps and outputs a prioritised list with paste-ready config snippets to close them. Covers hooks, CI, pre-commit, instruction file quality, init.sh, and session discipline. Use when starting a new project, auditing an existing harness, writing or reviewing CLAUDE.md/AGENTS.md, setting up CI gates, beginning multi-day autonomous work, or when user says "set up harness", "health check", "agent discipline", "project setup", "pre-commit hooks", "stop hook", "verification gap".
---

# Harness Engineering

Scan → Interview → Output. Build the complete gap list before generating any output.

Read `references/scenarios.md` first — it contains scenario-specific rules (CLAUDE.md guidance, brownfield, multi-day scope, Kiro/Gemini, gsd-2) that override defaults.

## Phase 1 — Detect

See `references/detect.md` for the full checklist. Run **all** checks before producing output.

1. **Runtime** (run first): `.claude/` → Claude Code · `.kiro/` → Kiro · `.gemini/` → Gemini · none → ask in Phase 2
2. **Hooks**: `.claude/settings.json` — Stop + PostToolUse present? **Always gap #1 if missing.**
3. **Stack**: `package.json` / `pyproject.toml` / `go.mod`
4. **CI**: `.github/workflows/*.yml` — runs lint + build?
5. **Pre-commit**: `.husky/` or `.pre-commit-config.yaml`
6. **Health script**: `init.sh` at root — exists and executable?
7. **Instruction file**: `CLAUDE.md` or `AGENTS.md` — treat as equivalent; never flag one missing when the other exists
8. **Rules dir**: `.claude/rules/` — present if instruction file exceeds 100 lines?
9. **Spec workflow**: `docs/superpowers/specs/` exists?
10. **Installed skills**: gsd-2 (apply mapping from `references/detect.md`); from this collection: `grill-me`, `grill-with-docs`, `write-a-skill`, `triage`, `to-prd`, `to-issues`, `context-handover`, `session-start`
11. **Onboarding config**: `docs/agents/` — exists with harness skill config files?
    → If yes: mark as "setup-harness-skills configured" in Already in Place.
    → If no: after the main gap list, append: "**Optional:** Run `/setup-harness-skills` to configure GitHub Project integration, session state tracking, and context handover — this extends the harness to cover long-running multi-session work."

Build two lists: **Already in place** · **Gaps**

## Phase 2 — Interview

Max 3 questions. Ask one at a time; wait for each answer.

**Q1 (always):** "Quick focused task (<1 hr) or longer autonomous work (multi-hour / multi-session)?"

**Q2 (conditional):**
- No runtime detected → "Which agent — Claude Code, Kiro, Gemini, other?" + "Solo or team? Greenfield or brownfield?"
- Runtime detected → "Solo or team? Existing codebase or starting fresh?"

**Q3 (only if 3+ major gaps):** "What matters most: stability gates (CI + hooks), session discipline (CLAUDE.md + hooks), or goal structure (autonomous tasks)?"

## Phase 3 — Output

**Rules — never violate:**
- Stop hook is **always gap #1** when `.claude/settings.json` absent. Nothing precedes it.
- AGENTS.md = CLAUDE.md — never flag CLAUDE.md missing when AGENTS.md present; apply quality checks to whichever exists.
- Brownfield: recommend `eslint --fix .` in one cleanup commit (ratchet) — never tell user to fix all errors manually.
- Multi-day scope: must include "one active task at a time", one anti-pattern by name (Fuzzy Done / Proxy Signal / Confidence Exit / Planning=Done), and a Judge audit as exit criterion.
- Max 5 gaps shown; note extras as lower priority.

**Structure:**
```
## Already in place
## Harness gaps (priority order)
### 1. [Gap name]
**Why it matters:** [failure mode — one sentence]
**Fix:** [paste-ready snippet]
...
## What to do next
```

Snippets: `references/universal-snippets.md` · `references/node-snippets.md` · `references/python-snippets.md` · `references/kiro-snippets.md`
