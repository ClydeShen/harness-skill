# Scenario-Specific Behavioral Rules

Apply these before Phase 1. Each rule fires on its stated condition.

---

## gsd-2 installed

When user mentions any `/gsd` command, treat gsd-2 as installed and apply both notes:

**Note A — init.sh gap (always, during gap analysis):**
Note `"/gsd doctor covers the init.sh health check — run it at the start of each session instead of a manual init.sh."` This closes the init.sh gap.

**Note B — Judge audit (only when task is multi-hour or longer):**
Include `"Use /gsd verdict pass|needs-attention|needs-remediation as your exit criterion — this is the Judge audit for gsd-2 users."` Add after main multi-day verification discipline advice — do not replace the general guidance.

---

## Multi-day / week-long tasks

When user mentions "a week", "week of work", "multi-day", or >1 day, output MUST include all four — use the exact terms:

1. **"one active task at a time"**: *"Work on one active task at a time — define clear done criteria before starting each task."*
2. **"Fuzzy Done"**: *"Watch out for Fuzzy Done — 'tests pass' is not the same as 'the feature works end-to-end in a real environment'."* (Also acceptable: Proxy Signal, Confidence Exit, Planning=Done)
3. **"Judge audit"**: *"Before declaring the goal complete, run a Judge audit — a skeptical re-read of all task outputs and observable behavior end-to-end."*
4. Completion proof must be **observable behavior** (walk through the feature manually), not just CI passing.

---

## CLAUDE.md / AGENTS.md content questions

When user asks what to include or leave out of CLAUDE.md or AGENTS.md, structure your response with **"What to leave out" first**, then "What to include".

**What to leave out (state all five explicitly):**

1. **Size budget**: *"Target ~60 lines. Hard ceiling: 200 lines. Past 100 lines? Move path-specific rules to `.claude/rules/`."*
2. **Code style**: *"Code style belongs in ESLint/Prettier, not in CLAUDE.md. If it's auto-enforceable, it has no place here."*
3. **Stale content** (use phrase "Delete resolved bugs"): *"Delete resolved bugs and past decisions — they rot and crowd out the rules Claude actually needs."*
4. **Deep docs** (use phrase "reference by file path"): *"Reference deep docs by file path (e.g., `@docs/api-spec.md`), never duplicate inline."*
5. **Task-specific rules** — show the `<important if='...'>` example:

```markdown
<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use existing test helpers — don't invent new patterns
</important>
```

**What to include:** tech stack (one line), key commands (dev/build/lint/test), architecture boundaries (2–3 sentences), non-obvious gotchas.

---

## Kiro runtime (`.kiro/` detected)

Output standard Claude Code gap analysis first, then append:

*"Kiro equivalents: `.kiro/hooks/` with `agentTurnEnd` trigger replaces the Stop hook; `postToolUse` trigger replaces PostToolUse hook. `.kiro/steering/` replaces CLAUDE.md. See `references/kiro-snippets.md` for paste-ready config."*

Do not restructure gap priority for Kiro.

---

## Gemini runtime (`.gemini/` detected)

Output standard Claude Code gap analysis first, then append:

*"Gemini equivalents: `GEMINI.md` at project root replaces CLAUDE.md (same template, same 200-line ceiling). Hook equivalents are not publicly documented — verify in your Gemini agent's settings. CI and init.sh recommendations apply universally."*

Do not restructure gap priority for Gemini.

---

## Brownfield / inherited codebase with lint errors

- Stop hook is still gap #1 — lint errors do not change this priority.
- For pre-commit hooks: *"Run `eslint --fix .` in a **single dedicated cleanup commit** to baseline existing violations. Then enable the pre-commit hook going forward — this is the ratchet approach."*
- Do NOT say the user must fix all errors manually before starting.
- Still mention hooks: `.claude/settings.json` with Stop and PostToolUse is still gap #1 even in brownfield — mention it explicitly.

---

## AGENTS.md present — user asks if CLAUDE.md is needed

1. Say: **"No. Claude Code reads AGENTS.md natively — it is equivalent to CLAUDE.md. You do not need a CLAUDE.md."**
2. Quality-check AGENTS.md: state line count, whether it's within 200-line ceiling, whether it uses `<important if="...">` tags.
3. Report other harness gaps normally.

---

## Interview branch decisions

### Q1 — Task scope

| Answer | What changes |
|---|---|
| **Quick (<1 hr)** | Show hooks + CLAUDE.md gaps only. Omit init.sh, goal structure, cross-session memory. |
| **Long / autonomous (>1 hr)** | Show all major gaps. Add init.sh to top-5. Add long-task verification discipline (one active task, anti-patterns, Judge audit, observable behavior). |

### Q2 — Team / Runtime

| Answer | What changes |
|---|---|
| **Solo** | CI: `push: branches: [main]` only. No branch protection recommendation. |
| **Team** | CI: add `pull_request: branches: [main]`. Add branch protection note. |
| **Brownfield** | Apply brownfield ratchet (see section above). |
| **Kiro** | Apply Kiro runtime rules (see section above). |
| **Gemini** | Apply Gemini runtime rules (see section above). |

### Q3 — Priority (3+ gaps only)

| Answer | Lead with |
|---|---|
| **Stability gates** | hooks snippet, then CI |
| **Session discipline** | hooks snippet, then CLAUDE.md template |
| **Goal structure** | init.sh snippet, then goal board / Judge audit guidance |

---

## CLAUDE.md skill substitutions

When outputting the CLAUDE.md template, replace behavior lines with installed skill triggers:

| Installed skill | Behaviour phrase | Replace with |
|---|---|---|
| gsd-2 `/gsd discuss` | `explore intent and tradeoffs before writing any code` | `` `/gsd discuss` `` |
| `grill-me` | `explore intent and tradeoffs before writing any code` | `` `/grill-me` skill `` |
| gsd-2 `/gsd auto` | `write a step-by-step plan before touching files` | `` `/gsd` (step mode) or `/gsd auto` (autonomous) `` |

When gsd-2 and `grill-me` are both installed, use gsd-2 and omit the `grill-me` row.
