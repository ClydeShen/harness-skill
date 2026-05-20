---
name: harness-engineering
description: >
  Detects harness gaps in a project and produces paste-ready config snippets to
  close them. Covers Stop and PostToolUse hooks, CI pipeline, pre-commit,
  CLAUDE.md/AGENTS.md quality, init.sh, and session discipline. Use when
  starting a coding session, setting up quality gates, writing or auditing
  CLAUDE.md or SKILL.md files, beginning long autonomous work (>1 hr), or
  after a session left in broken state. Triggers on: "start session", "set up
  harness", "how should I structure this task", "CI pipeline", "pre-commit
  hooks", "writing CLAUDE.md", "goal structure", "sprint contract",
  "verification gap", "health check", "harness setup", "project setup",
  "agent discipline".
---

## Scenario-Specific Required Content

Apply these before generating output — they override training defaults.

### Multi-day / week-long tasks
When user mentions "a week", "week of work", "multi-day", or >1 day, include **all four** of these in your response — use the exact terms:

**1.** Use the phrase **"one active task at a time"**: *"Work on one active task at a time — define clear done criteria before starting each task."*

**2.** Use the term **"Fuzzy Done"**: *"Watch out for Fuzzy Done — 'tests pass' is not the same as 'the feature works end-to-end in a real environment'."* (You may also name: **Proxy Signal**, **Confidence Exit**, **Planning=Done**)

**3.** Use the term **"Judge audit"**: *"Before declaring the goal complete, run a Judge audit — a skeptical re-read of all task outputs and observable behavior end-to-end. This is the only valid exit criterion."*

**4.** Completion proof must be **observable behavior** (walk through the feature manually), not just CI passing or tests green.

### CLAUDE.md / AGENTS.md content questions
When user asks what to include or leave out of CLAUDE.md or AGENTS.md, include ALL of the following in your response (use these exact sentences):

**Size budget (output this):** "Target ~60 lines. Hard ceiling: 200 lines per file. If you hit 100, move path-specific rules to `.claude/rules/`."

**Leave out — state each of these explicitly:**
- "Code style rules (spacing, naming, formatting) belong in ESLint/Prettier, NOT in CLAUDE.md. If it's auto-enforceable, it has no place here."
- "Delete resolved bugs and past decisions — they rot and crowd out the rules Claude actually needs."
- "Reference deep docs by `@file-path` (e.g., `@docs/api-spec.md`), never duplicate inline. CLAUDE.md is an index, not a copy."

**Conditional tags — output this exact example:**
```markdown
<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use existing test helpers — don't invent new patterns
</important>
```

**Also include:** Non-obvious gotchas that would bite an experienced developer who doesn't know the codebase.

### Gap analysis when .claude/settings.json is absent
When `.claude/settings.json` is missing from the project or user says there is no `.claude/settings.json`:

**Stop hook MUST be listed FIRST** in your gap list, regardless of format (table row or numbered section). No other gap — not CLAUDE.md size, not CI, not ESLint errors — may appear before it.

The JSON snippet from the Phase 3 template must appear in your response (paste it directly — not just a reference to it).

### Brownfield / inherited codebase with lint errors
When user inherits a codebase with many existing ESLint errors:

- Stop hook is still gap #1 — lint errors don't change this priority.
- For pre-commit hooks: say *"Run `eslint --fix .` in a **single dedicated cleanup commit** to baseline existing violations. Then enable the pre-commit hook going forward — this is the ratchet approach."*
- Do NOT say the user must fix all errors manually before starting.

### AGENTS.md present — user asks if CLAUDE.md is needed
When the project has AGENTS.md and user asks whether they need CLAUDE.md:
1. Say: **"No. Claude Code reads AGENTS.md natively — it is equivalent to CLAUDE.md. You do not need a CLAUDE.md."** Do NOT say that Claude Code only reads CLAUDE.md. Do NOT recommend creating CLAUDE.md.
2. Quality check AGENTS.md — say: *"AGENTS.md: [N] lines — [within/over] the 200-line ceiling. [Uses/No] `<important if='...'>` conditional tags. If it grows past 100 lines, use `.claude/rules/` for path-specific rules."*
3. Report other harness gaps (hooks, CI, init.sh, etc.) normally.

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

**Run ALL 10 checks and build the complete gap list before generating any output. Do not stop at the first gap found.**

1. Check Claude hooks: `.claude/settings.json` — PostToolUse + Stop hooks present? ← **always first**
2. Identify stack: look for `package.json`, `pyproject.toml`, `go.mod`
3. Check CI: `.github/workflows/*.yml` — does it run lint + build?
4. Check pre-commit: `.husky/` or `.pre-commit-config.yaml`
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
| **Long / autonomous (>1 hr)** | Show all major gaps. Add init.sh to top-5 if missing. After the gap list: (1) add a note about cross-session memory and running `init.sh`; (2) include long-task verification discipline (see section below). |

### Q2 — Team size

| Answer | What changes in output |
|---|---|
| **Solo** | CI snippet uses `push: branches: [main]` trigger only. Do not recommend branch protection rules, PR review gates, or `pull_request` trigger. |
| **Team** | CI snippet adds `pull_request: branches: [main]` trigger. Add a note: "Consider adding branch protection on main (require PR + passing CI before merge)." |
| **Brownfield (inherited codebase)** | Do NOT tell the user to fix all existing lint errors before starting. Explain the ratchet approach: run `eslint --fix` (or equivalent) in a single dedicated cleanup commit to reduce noise, then enable the pre-commit hook going forward. Stop hook is still the #1 gap regardless. |

### Long-task verification discipline (include when Q1 = long/autonomous)

Warn explicitly about these failure modes when surfacing goal structure guidance:

- **Fuzzy Done** — "tests pass" is not the same as "feature works end-to-end"
- **Proxy Signal** — build success is not behavior confirmation
- **Confidence Exit** — Claude's self-declared done is not evidence of done
- **Planning=Done** — a written plan is not completed work

Recommend: one active task at a time; require observable end-to-end behavior check (not just tests passing or build succeeding) before marking any task done; final **Judge audit** (skeptical re-read of ALL task outputs and behavior) before the overall goal is declared complete — this is the only valid exit criterion. Cross-session memory (`MEMORY.md` or memobank) + `init.sh` are the minimum resumption kit.

---

### Q3 — Priority (only fires with 3+ major gaps)

| Answer | What changes in output |
|---|---|
| **Stability gates** (CI and hooks) | Lead with `.claude/settings.json` hooks snippet, then CI. Move CLAUDE.md and init.sh gaps to "lower priority" section. |
| **Session discipline** (CLAUDE.md and hooks) | Lead with `.claude/settings.json` hooks snippet, then CLAUDE.md template. Move CI and init.sh to "lower priority" section. |
| **Goal structure** (autonomous tasks) | Lead with init.sh snippet, then add Goal structure guidance: Sprint Contract for <1 day; full goal board for multi-session; and a final **Judge audit** (skeptical re-read of all task outputs and observable behavior) before declaring the overall goal complete. Move CI and hooks to "lower priority" section. |

---

## Phase 3 — Output

Produce a single response after the interview. The structure must be:

**## Already in place**
- [each detected item, one line each]

**## Harness gaps (priority order)**

**### 1. No Stop hook** ← MANDATORY FIRST when .claude/settings.json is absent
**Why it matters:** Claude declares done without verifying — the most common failure mode.
**Fix:** Create `.claude/settings.json` with the following content (swap `npx eslint --fix` for your stack's linter):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\""}]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before ending this turn: (1) Run the project build and lint — fix any errors now, not later. (2) If this was UI work, open the feature in a browser and confirm the behavior is observable end-to-end. (3) Write a two-sentence status summary: what was changed and what the next concrete step is. Complete all outstanding checks before finishing."
          }
        ]
      }
    ]
  }
}
```

**### 2. No PostToolUse hook** ← always second if missing (same settings.json fixes both)
...

**### 3.** [Next gap in order]
...

**## What to do next**
[1–2 sentences: suggested order of attack]

**Output rules:**
- **Stop hook is ALWAYS gap #1** if missing — never put CLAUDE.md, CI, or any other gap before it. No exceptions.
- When `.claude/settings.json` is absent: list Stop hook as gap #1 and PostToolUse hook as gap #2. The settings.json JSON snippet above in this template is your starting point — output it directly.
- If `AGENTS.md` is present (with no `CLAUDE.md`): the instruction file gap is **CLOSED** — do NOT suggest creating `CLAUDE.md`. Do NOT explain differences between them. Apply quality checks to `AGENTS.md`: explicitly state its line count, confirm whether it is within the 200-line ceiling, note if it uses `<important if="...">` conditional tags, mention `.claude/rules/` as an option if it grows past 100 lines. Report other gaps normally.
- For "No agent instruction file" gap OR when user asks about CLAUDE.md content: apply the full **CLAUDE.md Guidance** section (below) — it contains the size budget, include/exclude rules, and conditional-tags example. State all exclusion rules explicitly: size budget, code style → linter, delete resolved bugs, reference docs by path, use conditional tags for task-specific rules.
- For brownfield / inherited codebase: do **NOT** tell the user to fix all existing lint errors. Instead: run `eslint --fix` in a single dedicated cleanup commit to baseline lint noise, then enable the hook going forward. This is the ratchet approach.
- When the user describes work as "a week", "week of work", "weeks", "multi-day", or >1 day: treat as long/autonomous scope immediately. The output MUST include: (1) one active task at a time with explicit task boundaries; (2) at least one verification anti-pattern by name (Fuzzy Done, Proxy Signal, Confidence Exit, Planning=Done); (3) a final **Judge audit** — skeptical re-read of ALL outputs and observable behavior — as the required exit criterion before declaring the goal complete.
- Session-start / pre-task guidance MUST include: read the relevant spec or documentation before writing any code.
- Spec workflow (`docs/superpowers/specs/` absent) is a **minor gap by default** but escalates to **major gap** when Q1 answer is "long / autonomous (>1 hr)"
- Each snippet is complete and paste-ready — no `YOUR_PROJECT_NAME`; use sensible defaults with inline comments marking what to customise
- Node/TS and Python: load the relevant helper file for stack-specific snippets
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

## CLAUDE.md Guidance

Apply this section whenever:
- The user asks "what should I include / leave out of CLAUDE.md?"
- The "No agent instruction file" gap is being addressed
- The user is auditing or writing a CLAUDE.md / AGENTS.md

### Size budget

**Target: 60 lines. Hard ceiling: 200 lines per file.**

If the file grows past 100 lines, move path-specific rules to `.claude/rules/` — files there load only when matching paths are opened, not on every turn.

### What to include

- **Tech stack** — one line (e.g., `Next.js 14 · TypeScript · Supabase · Stripe`)
- **Key commands** — the exact scripts Claude needs: dev server, build, lint, type-check, test
- **Architecture boundaries** — 2–3 sentences on key constraints (not a file tree)
- **Gotchas** — non-obvious traps only; things that would bite an experienced developer who doesn't know this codebase

### What to leave out (tell the user explicitly)

- **Code style** → belongs in the linter (ESLint / Prettier config), **not** in CLAUDE.md. If it's auto-enforceable, it has no place here.
- **Resolved bugs and past decisions** → delete them. They rot and crowd out the rules Claude actually needs.
- **Ephemeral session content** → task lists, in-progress notes, PR summaries — none of this belongs in CLAUDE.md.
- **Deep specs and long docs** → reference by file path (`@docs/api-spec.md`), never duplicate inline. CLAUDE.md is an index, not a copy.
- **Task-specific rules** → put these in `<important if="...">` conditional tags or `.claude/rules/` files, not in the always-loaded main body. Loading everything every turn crowds out foundational rules.

### Conditional tags — always show this example

Task-specific rules should use conditional tags so they only load when relevant:

```markdown
<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use existing test helpers — don't invent new patterns
</important>

<important if="you are editing a route handler or API endpoint">
- Auth check must be the first operation
- Return `{ data: T }` on success, `{ error: string }` on failure
</important>
```

---

## Reference: Session Lifecycle & Best Practices

For full session lifecycle, goal structure, verification discipline, context
window management, and CLAUDE.md quality rules — these are available in the
project's engineering standards document. Reference it when the user asks for
deeper guidance beyond the gap checklist.
