---
name: harness-engineering
description: >
  Use this skill whenever starting a coding session, setting up quality gates,
  writing or auditing CLAUDE.md or SKILL.md files, beginning any task that will
  run autonomously for more than one hour, or after a session left in a broken
  state. Trigger on: "start session", "set up harness", "how should I structure
  this task", "beginning work on", "session start", "long-running task", "set up
  quality gates", "CI pipeline", "pre-commit hooks", "what do I need before I
  start", "how do I keep claude on track", "agent discipline", "writing CLAUDE.md",
  "goal structure", "sprint contract", "verification gap". Use this skill even if
  the user doesn't say "harness" — any session-start or task-structure question
  qualifies.
---

## Pre-Execution Checklist

Before writing the first line of feature code, confirm all of these. Do not trade resolution for speed.

1. **Environment health gate** — run the project's health check script; do not proceed if it exits non-zero
2. **Clean baseline** — run lint and build; if either fails, fix it first. Never build on a broken base
3. **Known-good state** — confirm the working tree is clean or WIP is intentional
4. **Relevant spec exists** — read the spec for the thing being implemented; if none exists for a task over ~1 hour, write one first
5. **Scope defined** — list which files are in scope before touching anything
6. **Done criteria agreed** — negotiate a Sprint Contract: which specific files change, which commands prove it works, which user-visible behaviour confirms completion

---

## Session Lifecycle

Three phases. Do not skip or collapse them.

### Phase 1 — Init

```
1. Run environment health check
2. Load cross-session memory (memobank or equivalent)
3. git status — confirm clean tree or documented WIP
4. Run lint + build — verify baseline passes before any changes
5. Read the relevant spec for today's work only (not all docs)
6. Create or resume task tracking entries
7. For tasks >~1 hour: conduct Initial Interview before writing code
```

**Initial Interview (6 items):**

1. Full project context — where does this fit in the larger system?
2. What bad looks like — data loss, broken auth, broken contracts, regression
3. Prior attempts and traps — what has been tried? what went wrong?
4. Known gotchas in this area of the codebase
5. Open unknowns — ask the user explicitly before proceeding
6. **Sprint Contract** — agree on the exact finish line: which files change, which commands prove it works, which user-visible signal confirms done

Only start coding after the user confirms. The interview is an alignment gate, not a formality. The Sprint Contract is the most important output — without it, "done" is undefined.

### Phase 2 — Execute

- One task in progress at a time — no task-switching mid-feature
- Skill gate sequence: brainstorm → plan → implement → verify
- Commit after each meaningful unit of work — small, scoped, traceable
- Never declare done without running the full verification sequence

### Phase 3 — Wrap-Up

```
1. Run build — confirm still passes
2. Run lint — confirm no regressions
3. git status — no unintentional unstaged changes
4. Mark tasks done in task tracking
5. Save learnings to cross-session memory
6. Update CLAUDE.md if harness decisions changed this session
```

---

## Goal Structure (Tasks >~1 Hour)

Use a structured goal board. Do not use it for a one-change task — task tracking is sufficient.

### Four Primitives

| Primitive | What it is |
|---|---|
| **Charter** | Human-editable; describes what this tranche must accomplish |
| **Board** | Machine truth; wins if charter and board conflict |
| **Task** | One entry on the board; exactly one active at a time |
| **Receipt** | Compact durable proof the task happened; stored on the task card |

### Required Intake (fill before starting)

| Field | Question it answers |
|---|---|
| Objective | What specific outcome must become true? |
| Non-Negotiable Constraints | What must not change or break? |
| Completion Proof | Observable signal proving full outcome is done — not a proxy signal |
| Likely Misfire | How could the AI succeed at the wrong thing? Force this question. |
| Stop Rule | Stop only when a final audit receipt says `full_outcome_complete: true` |

If Completion Proof and Stop Rule cannot be filled before starting, the task is not ready to execute.

### Roles

| Role | Write Access | Use For |
|---|---|---|
| Scout | None — read only | Mapping, finding evidence, identifying candidates |
| Judge | None — read only | Choosing next slice, reviewing completed work, final audit |
| Worker | Only inside declared `allowed_files` | Executing one bounded slice; leaves receipt |
| PM | Control files only | Owning the board, choosing active tasks |

Judge decides; Worker executes. No implementation without an active Worker task naming `allowed_files`.

### Slice Sizing

A good task is the largest safe useful slice — not the smallest. Safe means bounded, explicit, verified, reversible. Two consecutive tiny tasks with no behaviour change means the board needs reorientation.

### Continuation Rule

After a task completes, immediately select the next unless a final Judge audit proves `full_outcome_complete: true`. Blocked ≠ stop: mark the specific task blocked and continue safe local work.

### Mission Pattern (Multi-Session Tasks)

For tasks that span sessions or require waiting for external feedback:

1. Write a note: current hypothesis, what was tried, artifact produced, what to check next session
2. Execute one step: hypothesis → action → artifact
3. Suspend — do not spin-wait; schedule next check at a realistic interval
4. Human escalation gate: surface to user before any dramatic or irreversible action

---

## Verification Discipline

A task is not done until build exits 0, lint exits 0, and the feature has been observed running. Belief is not evidence. Run the build; open the browser.

### Anti-Patterns

| Anti-pattern | What it looks like | Why it fails |
|---|---|---|
| **Fuzzy Done** | "Fix the bugs" · "Improve UX" | Unquantifiable; AI exits at first plausible-looking state |
| **Proxy Signal** | "Compile passes" · "One test passes" | Passing ≠ working; real validation still required |
| **Planning = Done** | "Plan is ready" · "Scout complete" | Planning is not completion; implementation + audit required |
| **Confidence Exit** | "I believe this is correct" | Belief is not evidence; run the build, open the browser |

---

## Context Window Management

Act before reaching degradation — not after.

| Usage | State | Action |
|---|---|---|
| < 30% | Healthy | Continue normally |
| 30–40% | Warning | Offload expensive ops to subagents; avoid loading large files |
| 40%+ | Degradation zone | Intelligence drops here; `/compact` or delegate to subagent now |
| > 60% | Simple tasks only | `/clear` + structured handoff for anything complex or high-risk |

**`/compact` vs Context Reset:** `/compact` is lossy but keeps momentum. Context Reset (`/clear` + handoff file) eliminates context anxiety — the failure mode where models declare completion prematurely as they approach token limits. Use Reset for long-running or high-risk sessions.

---

## CLAUDE.md Quality Rules

**Size:** Target 60 lines; 200 is the hard ceiling per CLAUDE.md file. Every line over 60 degrades all rules uniformly. The system prompt already occupies ~50 instruction slots — CLAUDE.md competes for the remainder, so keep it tight.

**What belongs:**
- Tech stack and key commands
- Architecture hard boundaries
- File:line pointers (not code snippets — snippets go stale)
- Real gotchas that will bite someone
- Skill trigger reminders
- References to deep specs (never duplicated inline)

**What does not belong:**
- Code style rules — that is the linter's job, not CLAUDE.md's
- Task-specific guidance (goes in `/commands` or `docs/`)
- Resolved bugs, past session state, ephemeral decisions

**Progressive disclosure:** CLAUDE.md always loaded → design/style anchor before UI work → feature specs on demand → architecture docs on demand. Never load all docs upfront.

**Conditional tags for task-specific rules:**

```markdown
<important if="you are writing or modifying tests">
- Use the project's test factory helpers, not raw fixtures
- Run the full test suite before marking done
</important>
```

Conditions must be narrow ("writing or modifying tests") not broad ("writing code"). Do not wrap foundational content — those rules apply always.

---

## Hooks

Two hooks close the verification loop mechanically — no relying on memory.

**PostToolUse (Edit | Write):** Run the project's auto-fix linter on the modified file. Claude never manually triggers linting — the hook does it.

**Stop:** Prompt Claude to verify before declaring done — build, lint, and visual check (for UI work) must all be confirmed before the turn ends.

Together: verification is a machine property, not a memory property.

---

## Long-Term Harness

### Cross-Session Memory

- **Session start:** read the memory index; load relevant memories before any work begins
- **Session end:** save new learnings — preferences, decisions, validated approaches, corrections
- **Save:** user profile · feedback (corrections + validations) · project decisions · reference locations
- **Never save:** code patterns (in the code), debugging solutions (in commit messages), ephemeral session state

### Machine Gates (all must be present before complex feature work)

| Gate | What it catches |
|---|---|
| Pre-commit linter (staged files) | Style violations; auto-fixes trivial ones |
| Pre-commit type check (whole project) | Cross-file type errors before commit |
| CI lint | Anything auto-fix silently masked |
| CI build | Import errors, missing modules, build-time failures |

### Skill Writing Rules

| Rule | Detail |
|---|---|
| **Description = trigger condition** | "When should I fire?" not "What does this do?" — it is the routing signal |
| **Gotchas section mandatory** | Only real failure points that surprised someone; never state the obvious |
| **Goals and constraints, not prescriptions** | Tell the skill what to achieve and avoid; do not railroad with steps |
| **No obvious statements** | If a senior engineer would say "of course", cut it |
| **`context: fork`** | Add to frontmatter for skills that run in isolated subagents |
