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

Before asking any questions, scan the project. Read `references/detect.md` for
the full target list and interpretation guide.

**Run these checks:**
1. Identify stack: look for `package.json`, `pyproject.toml`, `go.mod`
2. Check CI: `.github/workflows/*.yml` — does it run lint + build?
3. Check pre-commit: `.husky/` or `.pre-commit-config.yaml`
4. Check Claude hooks: `.claude/settings.json` — PostToolUse + Stop hooks present?
5. Check health script: `init.sh` at root — exists and executable?
6. Check agent instruction file: `CLAUDE.md` OR `AGENTS.md` present? Check whichever exists: line count under 200? contains `<important if>` tags or `.claude/rules/`?
7. Check rules directory: `.claude/rules/` — exists if the instruction file is over 100 lines?
8. Check spec workflow: `docs/superpowers/specs/` directory exists?
9. Check UI harness (frontend stack only): `DESIGN.md` exists?
10. Check installed skills: which of the following are available in the current session?
    `brainstorming`, `systematic-debugging`, `writing-plans`, `simplify`,
    `freeze`, `careful`, `guard`, `using-git-worktrees`

Build two lists: **already in place** and **gaps**.

---

## Phase 2 — Interview

Ask only what the file scan could not determine. Maximum 3 questions. Ask one
at a time and wait for the answer before asking the next.

**Q1 — Always ask:**
> "Is this for a quick focused task (under ~1 hour) or longer autonomous work
> (multi-hour or multi-session)?"

**Q2 — Ask only if no branch protection or PR workflow detected:**
> "Solo dev or team? And is this an existing codebase you're inheriting, or starting from scratch?"

**Q3 — Ask only if 3 or more major gaps found:**
> "You're missing several components. What matters most right now: stability
> gates (CI and hooks), session discipline (CLAUDE.md and hooks), or goal
> structure (for autonomous tasks)?"

Skip Q3 if fewer than 3 major gaps — just rank by impact and present all.

---

## Interview Branch Decisions

Use this table after the interview to determine what to include or emphasise in Phase 3.

### Q1 — Task scope

| Answer | What changes in output |
|---|---|
| **Quick task (<1 hr)** | Show hooks + CLAUDE.md gaps only. Omit init.sh, Goal structure, cross-session memory — note them as "lower priority for quick tasks" if detected as gaps. Sprint Contract is the only session-discipline recommendation. |
| **Long / autonomous (>1 hr)** | Show all major gaps. Add init.sh to top-5 if missing. After the gap list, add a one-line note: "For multi-session work, also set up cross-session memory (MEMORY.md or memobank) and run `init.sh` at the start of every session." |

### Q2 — Team size

| Answer | What changes in output |
|---|---|
| **Solo** | CI snippet uses `push: branches: [main]` trigger only. Do not recommend branch protection rules, PR review gates, or `pull_request` trigger. |
| **Team** | CI snippet adds `pull_request: branches: [main]` trigger. Add a note: "Consider adding branch protection on main (require PR + passing CI before merge)." |
| **Brownfield (inherited codebase)** | Soften pre-commit recommendation: add hooks incrementally rather than fixing all existing violations at once. Suggest a dedicated cleanup commit to baseline lint errors before enabling the hook. |

### Q3 — Priority (only fires with 3+ major gaps)

| Answer | What changes in output |
|---|---|
| **Stability gates** (CI and hooks) | Lead with `.claude/settings.json` hooks snippet, then CI. Move CLAUDE.md and init.sh gaps to "lower priority" section. |
| **Session discipline** (CLAUDE.md and hooks) | Lead with `.claude/settings.json` hooks snippet, then CLAUDE.md template. Move CI and init.sh to "lower priority" section. |
| **Goal structure** (autonomous tasks) | Lead with init.sh snippet, then add Goal structure guidance (Sprint Contract for <1 day; full goal board for multi-session). Move CI and hooks to "lower priority" section. |

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
- Spec workflow (`docs/superpowers/specs/` absent) is a **minor gap by default** but escalates to **major gap** when Q1 answer is "long / autonomous (>1 hr)"
- Each snippet is complete and paste-ready — no `YOUR_PROJECT_NAME`; use
  sensible defaults with inline comments marking what to customise
- Node/TS and Python: load the relevant helper file for stack-specific snippets
- Universal gaps: load `references/universal-snippets.md`
- Maximum 5 gaps shown; if more exist, note them as lower priority at the end

**CLAUDE.md skill substitutions:**
The base CLAUDE.md template uses plain behavioral descriptions. When outputting
the template, replace each behaviour line with its skill trigger for every skill
confirmed installed in step 10. Leave the line unchanged if the skill is absent.

| Installed skill | Behaviour phrase to find | Replace end of line with |
|---|---|---|
| `brainstorming` | `explore intent and tradeoffs before writing any code` | `` `brainstorming` skill `` |
| `systematic-debugging` | `identify root cause before proposing a fix` | `` `systematic-debugging` skill `` |
| `writing-plans` | `write a step-by-step plan before touching files` | `` `writing-plans` skill; `/plan` for quick tasks `` |
| `simplify` | `review for dead code and overcomplication` | `` `simplify` skill `` |
| `freeze` | `limit edits to the affected directory until the fix is confirmed` | `` `freeze` skill `` |
| `careful` or `guard` | `warn and confirm before running` | `` `careful` / `guard` skill `` |
| `using-git-worktrees` | `use git worktrees` | `` `using-git-worktrees` skill `` |

For snippet content, read the appropriate reference file:
- Universal gaps → `references/universal-snippets.md`
- Node/TS stack → `references/node-snippets.md`
- Python stack → `references/python-snippets.md`

---

## Reference: Session Lifecycle & Best Practices

For full session lifecycle, goal structure, verification discipline, context
window management, and CLAUDE.md quality rules — these are available in the
project's engineering standards document. Reference it when the user asks for
deeper guidance beyond the gap checklist.
