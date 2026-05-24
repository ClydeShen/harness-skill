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

### gsd-2 harness-concept mappings
These two notes apply whenever gsd-2 is installed (user mentions any `/gsd` command). Apply them independently — each has its own trigger condition.

**Note A — init.sh gap (fire during gap analysis, regardless of task scope):**
When gsd-2 is installed and `init.sh` is absent or listed as a gap: note `"/gsd doctor covers the init.sh health check — run it at the start of each session instead of a manual init.sh."` This closes the init.sh gap.

**Note B — Judge audit exit criterion (fire only when task scope is multi-hour or longer):**
When gsd-2 is installed AND the task is multi-hour or longer: include `"Use /gsd verdict pass|needs-attention|needs-remediation as your exit criterion — this is the Judge audit for gsd-2 users."` Add this after your main multi-day verification discipline advice — do not let it replace the general guidance about one-active-task-at-a-time, observable behavior, and false completion warnings.

### Multi-day / week-long tasks
When user mentions "a week", "week of work", "multi-day", or >1 day, include **all four** of these in your response — use the exact terms:

**1.** Use the phrase **"one active task at a time"**: *"Work on one active task at a time — define clear done criteria before starting each task."*

**2.** Use the term **"Fuzzy Done"**: *"Watch out for Fuzzy Done — 'tests pass' is not the same as 'the feature works end-to-end in a real environment'."* (You may also name: **Proxy Signal**, **Confidence Exit**, **Planning=Done**)

**3.** Use the term **"Judge audit"**: *"Before declaring the goal complete, run a Judge audit — a skeptical re-read of all task outputs and observable behavior end-to-end. This is the only valid exit criterion."*

**4.** Completion proof must be **observable behavior** (walk through the feature manually), not just CI passing or tests green.

### CLAUDE.md / AGENTS.md content questions
When user asks what to include or leave out of CLAUDE.md or AGENTS.md, your response **MUST follow this structure exactly** — Leave Out first, then Include. Do NOT lead with what to include.

**Start your response with a "What to leave out" section containing ALL FIVE of these items:**

**1. Size budget** — write: *"Target ~60 lines. Hard ceiling: 200 lines per file. Approaching 100 lines? Move path-specific rules to `.claude/rules/`."*

**2. Code style** — write: *"Code style (spacing, naming, formatting) belongs in ESLint/Prettier, NOT in CLAUDE.md. If it's auto-enforceable, it has no place here."*

**3. Stale content** — write (use the phrase "Delete resolved bugs"): *"Delete resolved bugs and past decisions — they rot and crowd out the rules Claude actually needs."*

**4. Deep docs** — write (use the phrase "reference by file path"): *"Reference deep docs by file path (e.g., `@docs/api-spec.md`), never inline. CLAUDE.md is an index, not a copy."*

**5. Task-specific rules** — show the `<important if='...'>` conditional tag example:

```markdown
<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use existing test helpers — don't invent new patterns
</important>
```

**Then** cover what TO put in the file: key commands, tech stack (one line), architecture constraints (2–3 sentences), and non-obvious gotchas.

**Self-check before output:** Does your response contain all five leave-out items? Is "What to leave out" (or equivalent heading) the FIRST section? If not, restructure before finishing.

### Advisory guidance for Kiro runtime
When a `.kiro/` directory is detected (or user says they are using Kiro), add a brief **Kiro equivalents** note after your standard gap analysis:

*"Kiro equivalents: `.kiro/hooks/` with `agentTurnEnd` trigger replaces the Stop hook; `postToolUse` trigger replaces PostToolUse hook. `.kiro/steering/` replaces CLAUDE.md. See `references/kiro-snippets.md` for paste-ready config."*

Do not restructure gap priority for Kiro — output the standard Claude Code gap analysis first, then append the Kiro equivalents note.

### Gap analysis when .claude/settings.json is absent
When `.claude/settings.json` is missing from the project or user says there is no `.claude/settings.json`:

**Stop hook MUST be listed FIRST** in your gap list, regardless of format (table row or numbered section). No other gap — not CLAUDE.md size, not CI, not ESLint errors — may appear before it.

**NEVER put CLAUDE.md oversize as gap #1 when `.claude/settings.json` is missing** — even if CLAUDE.md is 500 lines. A bloated instruction file degrades rules; a missing Stop hook disables verification entirely. Degraded rules are recoverable; unverified work compounds silently. The Stop hook is always the more critical missing gate. List Stop hook as gap #1, CLAUDE.md oversize as gap #2 or lower.

**Use the exact terms**: Call the first gap **"Stop hook"** (not "hooks section", "hook configuration", or "settings.json setup"). Call the second gap **"PostToolUse hook"**. These are proper names — use them.

**If you mention Stop hook or PostToolUse hook as gaps, you MUST paste the full `.claude/settings.json` JSON snippet** — do not describe the fix without showing the config. Use the snippet from the Phase 3 template below (paste it directly).

### Advisory guidance for Gemini runtime
When a `.gemini/` directory is detected (or user says they are using Gemini), add a brief **Gemini equivalents** note after your standard gap analysis:

*"Gemini equivalents: `GEMINI.md` at project root replaces CLAUDE.md (same template, same 200-line ceiling). Hook equivalents are not publicly documented — verify in your Gemini agent's settings. CI and init.sh recommendations apply universally."*

Do not restructure gap priority for Gemini — output the standard Claude Code gap analysis first, then append the Gemini equivalents note.

### Brownfield / inherited codebase with lint errors
When user inherits a codebase with many existing ESLint errors:

- Stop hook is still gap #1 — lint errors don't change this priority.
- For pre-commit hooks: say *"Run `eslint --fix .` in a **single dedicated cleanup commit** to baseline existing violations. Then enable the pre-commit hook going forward — this is the ratchet approach."*
- Do NOT say the user must fix all errors manually before starting. **Why:** With hundreds of errors, manual fixes take days or weeks and block all productive work. `eslint --fix .` resolves the majority automatically in minutes. After that one baseline commit, the pre-commit hook enforces no new violations. The user can start using Claude Code today, not after weeks of cleanup.
- **ALWAYS also mention hooks**: `.claude/settings.json` with Stop and PostToolUse hooks is still gap #1 even in brownfield projects — mention it explicitly somewhere in your response. The lint ratchet handles pre-commit gating; it is a separate concern from hooks priority.

### AGENTS.md present — user asks if CLAUDE.md is needed
When the project has AGENTS.md and user asks whether they need CLAUDE.md:
1. Say: **"No. Claude Code reads AGENTS.md natively — it is equivalent to CLAUDE.md. You do not need a CLAUDE.md."** This is a factual behaviour of Claude Code: it reads AGENTS.md from the project root on every session start, the same as CLAUDE.md. Do NOT say that Claude Code only reads CLAUDE.md. Do NOT recommend creating CLAUDE.md.
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

**Run ALL checks and build the complete gap list before generating any output. Do not stop at the first gap found.**

0. **Detect runtime** ← run before everything else. Check for `.claude/`, `.kiro/`, `.gemini/` directories. Record detected runtime; if none found, mark as "unknown — ask in Phase 2". This determines which snippets load in Phase 3.
1. Check hooks for detected runtime:
   - Claude Code / Codex: `.claude/settings.json` — PostToolUse + Stop hooks present?
   - Kiro: `.kiro/hooks/` — postToolUse + agentTurnEnd hooks present?
   - Gemini / unknown: note hook gap as "verify in your agent's settings"
   ← **always first gap priority**
2. Identify stack: look for `package.json`, `pyproject.toml`, `go.mod`
3. Check CI: `.github/workflows/*.yml` — does it run lint + build?
4. Check pre-commit: `.husky/` or `.pre-commit-config.yaml`
5. Check health script: `init.sh` at root — exists and executable?
6. Check agent instruction file: `CLAUDE.md` OR `AGENTS.md` present? Check whichever exists: line count under 200? contains `<important if>` tags or `.claude/rules/`?
7. Check rules directory: `.claude/rules/` — exists if the instruction file is over 100 lines?
8. Check spec workflow: `docs/superpowers/specs/` directory exists?
9. Check UI harness (frontend stack only): `DESIGN.md` exists?
10. Check installed skills: which of the following are available in the current session?
    **gsd-2 (priority):** `/gsd` (step mode), `/gsd auto`, `/gsd discuss`, `/gsd quick`, `/gsd doctor`, `/gsd verdict`
    **Think before coding:** `brainstorming`, `systematic-debugging`, `writing-plans`
    **Simplicity:** `simplify`, `refactor-cleaner`, `vibe-code-auditor`, `health`
    **Surgical:** `freeze`, `careful`, `guard`, `using-git-worktrees`
    **Frontend:** `vercel-labs/agent-browser`

    If any gsd-2 command is available, treat gsd-2 as installed and apply harness-concept mapping (see `references/detect.md` — gsd-2 closes `init.sh` and Judge audit gaps).

Build two lists: **already in place** and **gaps**.

---

## Phase 2 — Interview

Ask only what the file scan could not determine. Maximum 3 questions. Ask one
at a time and wait for the answer before asking the next.

**Q1 — Always ask:**
> "Is this for a quick focused task (under ~1 hour) or longer autonomous work
> (multi-hour or multi-session)?"

**Q2 — Conditional (one of two forms):**

If Phase 1 step 0 found **no runtime signal** (no `.claude/`, `.kiro/`, `.gemini/`):
> "Which agent are you using — Claude Code, Kiro, Gemini, or something else?"
> Then ask the team/brownfield question as a follow-up within Q2.

If Phase 1 step 0 **identified the runtime** and no branch protection or PR workflow detected:
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

### Q2 — Team size / Runtime

| Answer | What changes in output |
|---|---|
| **Solo** | CI snippet uses `push: branches: [main]` trigger only. Do not recommend branch protection rules, PR review gates, or `pull_request` trigger. |
| **Team** | CI snippet adds `pull_request: branches: [main]` trigger. Add a note: "Consider adding branch protection on main (require PR + passing CI before merge)." |
| **Brownfield (inherited codebase)** | Do NOT tell the user to fix all existing lint errors before starting. Explain the ratchet approach: run `eslint --fix` (or equivalent) in a single dedicated cleanup commit to reduce noise, then enable the pre-commit hook going forward. Stop hook is still the #1 gap regardless. |
| **Runtime = Kiro** | Load `references/kiro-snippets.md` for all hook and instruction-file snippets. Gap #1 is "No agentTurnEnd hook" (not Stop hook — use Kiro terminology). Gap #2 is "No postToolUse hook". Instruction file gap points to `.kiro/steering/project.md`. |
| **Runtime = Gemini** | Output Claude Code snippets for universal gaps (CI, init.sh). For hook gaps: note "Gemini does not have a documented hook equivalent — verify in your Gemini agent's settings." For instruction file gap: recommend `GEMINI.md` using the CLAUDE.md template structure. |
| **Runtime = unknown (asked in Q2)** | Apply Kiro or Gemini branch as above once answered. If user names a runtime not in the list, default to Claude Code snippets with a note to adapt. |

### Long-task verification discipline (include when Q1 = long/autonomous)

Warn explicitly about these failure modes when surfacing goal structure guidance:

- **Fuzzy Done** — "tests pass" is not the same as "feature works end-to-end"
- **Proxy Signal** — build success is not behavior confirmation
- **Confidence Exit** — Claude's self-declared done is not evidence of done
- **Planning=Done** — a written plan is not completed work

Recommend: one active task at a time; require observable end-to-end behavior check (not just tests passing or build succeeding) before marking any task done; final **Judge audit** (skeptical re-read of ALL task outputs and behavior) before the overall goal is declared complete — this is the only valid exit criterion. Cross-session memory (`MEMORY.md` or memobank) + `init.sh` are the minimum resumption kit. If gsd-2 is installed, `/gsd doctor` replaces `init.sh` — run it at the start of each session; it covers the runtime health check gap.

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
- For "No agent instruction file" gap OR when user asks about CLAUDE.md content: apply the full **CLAUDE.md Guidance** section (below). **Cover Leave Out rules FIRST (before what to include)**: state all five explicitly — size budget, code style → linter, delete resolved bugs, reference docs by path, use conditional tags for task-specific rules — then describe what to include. Show the `<important if="...">` example.
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

**Priority rule:** when a gsd-2 skill and an equivalent superpowers skill are both installed, use the gsd-2 skill and omit the superpowers row.

| Installed skill | Behaviour phrase to find | Replace end of line with |
|---|---|---|
| gsd-2 `/gsd discuss` (priority) | `explore intent and tradeoffs before writing any code` | `` `/gsd discuss` `` |
| `brainstorming` | `explore intent and tradeoffs before writing any code` | `` `brainstorming` skill `` |
| `systematic-debugging` | `identify root cause before proposing a fix` | `` `systematic-debugging` skill `` |
| gsd-2 `/gsd auto` or `/gsd` (priority) | `write a step-by-step plan before touching files` | `` `/gsd` (step mode) or `/gsd auto` (autonomous) `` |
| `writing-plans` | `write a step-by-step plan before touching files` | `` `writing-plans` skill; `/plan` for quick tasks `` |
| `simplify` | `review for dead code and overcomplication` | `` `simplify` skill `` |
| `refactor-cleaner` | `remove dead code and unused imports` | `` `refactor-cleaner` skill `` |
| `vibe-code-auditor` | `audit AI-generated code for quality` | `` `vibe-code-auditor` skill `` |
| `health` | `check typecheck, lint, test, and dead code coverage` | `` `health` skill `` |
| `freeze` | `limit edits to the affected directory until the fix is confirmed` | `` `freeze` skill `` |
| `careful` or `guard` | `warn and confirm before running` | `` `careful` / `guard` skill `` |
| `using-git-worktrees` | `use git worktrees` | `` `using-git-worktrees` skill `` |
| `vercel-labs/agent-browser` (frontend only) | `detect and debug frontend issues in a real browser` | `` `vercel-labs/agent-browser` skill `` |

For snippet content, read the appropriate reference file:
- Universal gaps (Claude Code / Codex) → `references/universal-snippets.md`
- Kiro runtime → `references/kiro-snippets.md` (replaces universal hook snippets)
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

### What to leave out (cover these FIRST, before what to include)

- **Code style** → belongs in the linter (ESLint / Prettier config), **not** in CLAUDE.md. If it's auto-enforceable, it has no place here.
- **Resolved bugs and past decisions** → delete them. They rot and crowd out the rules Claude actually needs.
- **Ephemeral session content** → task lists, in-progress notes, PR summaries — none of this belongs in CLAUDE.md.
- **Deep specs and long docs** → reference by file path (`@docs/api-spec.md`), never duplicate inline. CLAUDE.md is an index, not a copy.
- **Task-specific rules** → put these in `<important if="...">` conditional tags or `.claude/rules/` files, not in the always-loaded main body. Loading everything every turn crowds out foundational rules.

### What to include

- **Tech stack** — one line (e.g., `Next.js 14 · TypeScript · Supabase · Stripe`)
- **Key commands** — the exact scripts Claude needs: dev server, build, lint, type-check, test
- **Architecture boundaries** — 2–3 sentences on key constraints (not a file tree)
- **Gotchas** — non-obvious traps only; things that would bite an experienced developer who doesn't know this codebase

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
