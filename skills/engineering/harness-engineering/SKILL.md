---
name: harness-engineering
description: Detects agent-harness gaps in a project and outputs paste-ready config snippets to close them. Covers Stop and PostToolUse hooks, CI, pre-commit, CLAUDE.md/AGENTS.md quality, init.sh, and session discipline. Use when starting a coding session, setting up quality gates, auditing CLAUDE.md, beginning long autonomous work, or after a session left in broken state. Triggers on: "start session", "set up harness", "CI pipeline", "pre-commit hooks", "writing CLAUDE.md", "goal structure", "verification gap", "health check", "harness setup", "project setup", "agent discipline".
---

# Harness Engineering

Scan → Interview → Output. Build the complete gap list before generating **any** output.

Read `references/scenarios.md` now — it contains scenario-specific behavioral overrides (gsd-2, CLAUDE.md guidance, brownfield, multi-day scope, Kiro/Gemini) that apply before Phase 1.

## Phase 1 — Detect

Read `references/detect.md` for the full target list and interpretation guide. Run **all** checks before producing any output.

1. **Runtime** (run first): `.claude/` → Claude Code; `.kiro/` → Kiro; `.gemini/` → Gemini; none → ask in Phase 2
2. **Hooks**: `.claude/settings.json` Stop + PostToolUse — **always gap #1 if missing**
3. **Stack**: `package.json`, `pyproject.toml`, `go.mod`
4. **CI**: `.github/workflows/*.yml` — runs lint + build?
5. **Pre-commit**: `.husky/` or `.pre-commit-config.yaml`
6. **Health script**: `init.sh` at root — exists and executable?
7. **Instruction file**: `CLAUDE.md` or `AGENTS.md` (equivalent — never flag CLAUDE.md missing when AGENTS.md present)
8. **Rules dir**: `.claude/rules/` — exists if instruction file is over 100 lines?
9. **Spec workflow**: `docs/superpowers/specs/` directory exists?
10. **Installed skills**: gsd-2, brainstorming, systematic-debugging, writing-plans, simplify, vercel-labs/agent-browser

Build two lists: **already in place** and **gaps**.

## Phase 2 — Interview

Max 3 questions, one at a time. Wait for each answer before asking the next.

**Q1 (always):** "Is this for a quick focused task (under ~1 hr) or longer autonomous work (multi-hour or multi-session)?"

**Q2 (conditional):**
- No runtime detected → "Which agent are you using — Claude Code, Kiro, Gemini, or something else?" + "Solo or team? Greenfield or brownfield?"
- Runtime detected → "Solo dev or team? And is this an existing codebase you're inheriting, or starting from scratch?"

**Q3 (only if 3+ major gaps):** "What matters most right now: stability gates (CI and hooks), session discipline (CLAUDE.md and hooks), or goal structure (for autonomous tasks)?"

## Phase 3 — Output

**Invariants — never violate:**
- **Stop hook is always gap #1** when `.claude/settings.json` absent. No other gap may precede it.
- **AGENTS.md = CLAUDE.md** — never flag CLAUDE.md missing when AGENTS.md present.
- **Brownfield**: never tell user to fix all lint errors manually. Recommend `eslint --fix .` in a single cleanup commit (ratchet approach).
- **Multi-day scope**: output MUST include "one active task at a time", at least one anti-pattern by name (Fuzzy Done / Proxy Signal / Confidence Exit / Planning=Done), and a Judge audit as the exit criterion.
- **Max 5 gaps** shown; note extras as lower priority.

**Output structure:**
```
## Already in place
## Harness gaps (priority order)
  ### 1. No Stop hook  ← mandatory first when .claude/settings.json absent
  ### 2–5. [remaining gaps]
## What to do next
```

Snippets: `references/universal-snippets.md` · `references/node-snippets.md` · `references/python-snippets.md` · `references/kiro-snippets.md`
