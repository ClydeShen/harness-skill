---
name: harness-engineering
description: >
  Use whenever starting a coding session, setting up quality gates, writing or
  auditing CLAUDE.md or SKILL.md files, beginning any task running autonomously
  for more than one hour, or after a session left in broken state. Trigger on:
  "start session", "set up harness", "how should I structure this task",
  "beginning work on", "session start", "long-running task", "set up quality
  gates", "CI pipeline", "pre-commit hooks", "what do I need before I start",
  "how do I keep claude on track", "agent discipline", "writing CLAUDE.md",
  "goal structure", "sprint contract", "verification gap", "health check",
  "harness setup", "project setup".
---

## Global Constraints

Apply these to every recommendation you make — prefer the simpler answer, the
smaller change, the fewer moving parts.

| Principle | Rule |
|---|---|
| **KISS** | Recommend the simplest solution that closes the gap. If a simpler path exists, say so first. |
| **YAGNI** | Only recommend gates the project has earned. No E2E tests on a solo MVP. |
| **DRY** | Flag duplication before introducing it. Shared config belongs in one place. |
| **First Principles** | Every gate must justify itself with a failure mode in one sentence. No failure mode = don't recommend it. |
| **Occam's Razor** | When two solutions close the same gap, recommend the one with fewer components and dependencies. |

---

## Phase 1 — Detect

Before asking any questions, scan the project. Read `helpers/detect.md` for
the full target list and interpretation guide.

**Run these checks:**
1. Identify stack: look for `package.json`, `pyproject.toml`, `go.mod`
2. Check CI: `.github/workflows/*.yml` — does it run lint + build?
3. Check pre-commit: `.husky/` or `.pre-commit-config.yaml`
4. Check Claude hooks: `.claude/settings.json` — PostToolUse + Stop hooks present?
5. Check health script: `init.sh` at root — exists and executable?
6. Check CLAUDE.md: exists? line count under 200? contains `<important if>` tags?
7. Check spec workflow: `docs/superpowers/specs/` directory exists?
8. Check UI harness (frontend stack only): `DESIGN.md` exists?

Build two lists: **already in place** and **gaps**.

---

## Phase 2 — Interview

Ask only what the file scan could not determine. Maximum 3 questions. Ask one
at a time and wait for the answer before asking the next.

**Q1 — Always ask:**
> "Is this for a quick focused task (under ~1 hour) or longer autonomous work
> (multi-hour or multi-session)?"

Use the answer to decide: Sprint Contract only, or full Goal structure + Mission
pattern recommendations.

**Q2 — Ask only if no branch protection or PR workflow detected:**
> "Solo dev or team?"

Use the answer to decide: CI strictness, branch workflow recommendations.

**Q3 — Ask only if 3 or more major gaps found:**
> "You're missing several components. What matters most right now: stability
> gates (CI and hooks), session discipline (CLAUDE.md and hooks), or goal
> structure (for autonomous tasks)?"

Skip Q3 if fewer than 3 major gaps — just rank by impact and present all.

---

## Phase 3 — Output

Produce a single response after the interview using this structure:

```
## ✓ Already in place
- [each detected item, one line each]

## Harness gaps (priority order)

### 1. [Gap name]
**Why it matters:** [one sentence — the specific failure mode this prevents]
**Fix:**
[filename or shell command]
[complete paste-ready content — no placeholders]

### 2. [Next gap]
...

## What to do next
[1–2 sentences: suggested order of attack]
```

**Output rules:**
- Rank gaps by impact: verification gap > CLAUDE.md quality > CI > pre-commit > memory
- Each snippet is complete and paste-ready — no `YOUR_PROJECT_NAME`; use
  sensible defaults with inline comments marking what to customise
- Node/TS and Python: load the relevant helper file for stack-specific snippets
- Universal gaps: load `helpers/universal-snippets.md`
- Maximum 5 gaps shown; if more exist, note them as lower priority at the end

For snippet content, read the appropriate helper file:
- Universal gaps → `helpers/universal-snippets.md`
- Node/TS stack → `helpers/node-snippets.md`
- Python stack → `helpers/python-snippets.md`

---

## Reference: Session Lifecycle & Best Practices

For full session lifecycle, goal structure, verification discipline, context
window management, and CLAUDE.md quality rules — these are available in the
project's engineering standards document. Reference it when the user asks for
deeper guidance beyond the gap checklist.
