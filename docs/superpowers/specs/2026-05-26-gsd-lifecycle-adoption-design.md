# GSD Lifecycle Adoption — Design Spec

**Date:** 2026-05-26
**Status:** Draft
**Scope:** Align this skill collection's artifact structure and phase vocabulary with GSD Redux (`open-gsd/get-shit-done-redux`), so projects using this collection produce GSD-compatible files natively. Installing GSD later requires zero migration.

---

## 1. Problem Statement

The current skill collection uses its own artifact locations (`.claude/session.json`, `.claude/handoff.md`, `.claude/harness.json`) and its own phase vocabulary (Design / Product / Execution / Testing). GSD Redux uses `.harness/STATE.md`, `.harness/phases/XX/.continue-here.md`, `.harness/config.json`, and the verbs discuss / plan / execute / verify.

Users who adopt this collection today and install GSD later must manually migrate all state artifacts. Users who run both simultaneously face two parallel session-state stores. The terminology mismatch (both systems call things "phases" but mean different things) creates confusion.

**Goal:** This collection generates GSD-compatible artifacts from day one. GSD can be installed at any time and pick up immediately with no migration.

---

## 2. Design Principles

| Principle | Application |
|---|---|
| **GSD-first artifacts** | When an artifact exists in GSD's schema, use GSD's exact path, file name, and template. Never invent a parallel format. |
| **Non-colliding extension** | This project adds its own configuration under a `harness` namespace inside `.harness/config.json`. GSD ignores unknown keys — no conflict. |
| **Graceful degradation** | Every skill works without GSD installed. It writes GSD-compatible files itself. GSD just reads them. |
| **YAGNI** | Only bridge what GSD actually uses. Don't invent adapter layers or translation utilities. |

---

## 3. File Mapping

### 3.1 Files that change location and/or format

| Before | After | Notes |
|---|---|---|
| `.claude/session.json` | `.harness/STATE.md` | GSD's living session state document |
| `.claude/handoff.md` | `.harness/phases/XX-name/.continue-here.md` | GSD's per-phase handoff; YAML frontmatter + XML sections |
| `.claude/harness.json` | `.harness/config.json` (`harness` key) | Extends GSD config; GSD ignores the `harness` key |
| `docs/superpowers/specs/*.md` | `.harness/phases/01-discuss/CONTEXT.md` | GSD 6-section CONTEXT.md format |
| `docs/superpowers/plans/*.md` | `.harness/phases/XX/XX-YY-PLAN.md` | GSD PLAN.md format |

### 3.2 Files that are NEW (written by `setup-harness-skills`)

| File | Template source | Purpose |
|---|---|---|
| `.harness/PROJECT.md` | GSD `templates/project.md` | Living project context (requirements, decisions, constraints) |
| `.harness/ROADMAP.md` | GSD ROADMAP format | Milestone + phase listing |
| `.harness/STATE.md` | GSD `templates/state.md` | Session state (replaces session.json) |
| `.harness/config.json` | GSD config defaults + `harness` namespace | Unified config |

### 3.3 Files that remain unchanged

| File | Reason |
|---|---|
| `docs/agents/` (all 5 seed files) | GitHub-integration config; GSD has no equivalent |
| `docs/adr/` | Project ADR archive; not a GSD concern |
| `.claude/settings.json` | Claude Code hooks; GSD does not manage this |
| `.github/workflows/ci.yml` | CI gate; GSD does not manage this |

### 3.4 `.harness/config.json` schema

GSD fields are used verbatim. The `harness` key is this project's extension:

```json
{
  "model_profile": "balanced",
  "commit_docs": true,
  "harness": {
    "schema_version": 1,
    "github": {
      "owner": "org",
      "repo": "project",
      "default_branch": "main",
      "project_v2_id": "PVT_xxxx",
      "project_board_name": "My Board"
    },
    "docs_agents_dir": "docs/agents",
    "issue_tracker": "github"
  }
}
```

**GSD ignores the `harness` key** — it validates only keys in its `VALID_CONFIG_KEYS` schema. The `harness` namespace is therefore safe to add at any time.

### 3.5 `.harness/STATE.md` schema

Written verbatim to GSD's template. This project's skills read and update only the **Session Continuity** section and the **Current Position** section:

```markdown
---
gsd_state_version: '1.0'
status: in_progress
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 0
  completed_plans: 0
  percent: 25
---

# Project State

## Project Reference

See: .harness/PROJECT.md (updated 2026-05-26)

**Core value:** [one-liner]
**Current focus:** 02-plan

## Current Position

Phase: 2 of 4 (02-plan)
Plan: 1 of N in current phase
Status: In progress
Last activity: 2026-05-26 — context handover

Progress: [██░░░░░░░░] 25%

## Session Continuity

Last session: 2026-05-26 14:30
Stopped at: [Description of last completed action]
Resume file: .harness/phases/02-plan/.continue-here.md
```

### 3.6 `.harness/phases/XX-name/.continue-here.md` schema

Written to GSD's exact template (YAML frontmatter + XML sections):

```yaml
---
phase: 02-plan
task: 2
total_tasks: 5
status: in_progress
last_updated: 2026-05-26T14:30:00Z
---
```

```xml
<current_state>
Where exactly are we?
</current_state>

<completed_work>
- Task 1: [name] — Done
- Task 2: [name] — In progress, [what's done]
</completed_work>

<remaining_work>
- Task 2: [what's left]
- Task 3: Not started
</remaining_work>

<decisions_made>
- Decided to use X because Y
</decisions_made>

<blockers>
None
</blockers>

<context>
Mental state and vibe to resume smoothly
</context>

<next_action>
Start with: [specific action]
</next_action>
```

---

## 4. Phase Vocabulary Rename

GSD uses the verbs discuss / plan / execute / verify for its workflow commands. This project renames its Design / Product / Execution / Testing stages to match:

| Old (this project) | New (GSD-aligned) | GSD command | Directory |
|---|---|---|---|
| Design | Discuss | `/gsd-discuss-phase` | `.harness/phases/01-discuss/` |
| Product | Plan | `/gsd-plan-phase` | `.harness/phases/02-plan/` |
| Execution | Execute | `/gsd-execute-phase` | `.harness/phases/03-execute/` |
| Testing | Verify | `/gsd-verify-work` | `.harness/phases/04-verify/` |

**GSD's "phase" (numbered chunk) vs this project's "stage" (workflow position):** GSD numbers its implementation chunks phase 1, phase 2, etc. within a milestone. This project maps those to fixed directory slots 01-discuss through 04-verify. No naming collision because GSD's phase numbering happens inside this project's stage directories when GSD plans work within a stage.

---

## 5. Skill-by-Skill Changes

### 5.1 `setup-harness-skills`

**What changes:**

Step 1 (Explore) — additionally reads:
- `.harness/config.json` (prior GSD or harness setup)
- `.harness/STATE.md` (prior session state)
- `.harness/PROJECT.md` (prior project context)

Section A.5 (Instruction file) — unchanged.

Section D (GitHub Project board) — add note: "GSD manages its build loop in `.harness/`. The GitHub Project board provides human visibility. Both are recommended. If GSD is later installed it will read `.harness/config.json` directly."

Section E (Session state) — changes from `.claude/session.json` to: "`.harness/STATE.md` follows GSD's format. Install GSD at any time and it reads this file directly."

**Output (what gets written):**

1. `.harness/config.json` — GSD defaults + `harness` namespace (idempotent merge)
2. `.harness/STATE.md` — from GSD state template (only if absent)
3. `.harness/PROJECT.md` — from GSD project template (only if absent)
4. `.harness/ROADMAP.md` — stub with four stage entries (only if absent)
5. `docs/agents/` — all 5 seed files (unchanged)
6. GitHub labels + milestones + branch protection (unchanged)

**gitignore additions:**
```
.harness/phases/*/.continue-here.md   # handoff docs — never commit
```
**What IS committed** (`commit_docs: true` by default, same as GSD):
- `.harness/STATE.md` — team-shared session state
- `.harness/config.json` — team-shared project config
- `.harness/PROJECT.md` — project context document
- `.harness/ROADMAP.md` — milestone and phase listing
- `.harness/phases/*/CONTEXT.md` — discuss-phase decisions (written by `to-prd`)
- `.harness/phases/*/PLAN.md` — plan tasks (written by `to-issues`)

**What is NOT committed:**
- `.harness/phases/*/.continue-here.md` — ephemeral per-session handoff; deleted on resume by GSD convention

**What does NOT change:** The 6-section setup interview (A through E), the GitHub label creation, the branch protection, the CI scaffold, the docs/agents/ seed files. The interaction model is identical.

### 5.2 `session-start`

**Recovery chain (replaces four-tier chain):**

```
1. Read .harness/STATE.md
   → Session Continuity.Resume file → path to .continue-here.md
   → Current Position → phase, plan, status, last activity

2. Read .harness/phases/XX-name/.continue-here.md (path from STATE.md)
   → <next_action> is the pick-up point
   → <completed_work> and <remaining_work> reconstruct context

3. Git log reconstruction (fallback when .continue-here.md deleted or stale)
   → git log --oneline -20
   → Recent GitHub progress comments (if docs/agents configured)

4. Cold start (nothing found)
   → "No prior session state found."
   → Present what WAS found
   → Suggest: "Run /setup-harness-skills to initialize .harness/"
```

**Phase skip/revert (artifact-observable only):**

| Condition | Action |
|---|---|
| `.harness/phases/01-discuss/` contains a `CONTEXT.md` | Skip Discuss — set to Plan |
| `.harness/phases/02-plan/` contains a `PLAN.md` | Skip Discuss + Plan — set to Execute |
| `.harness/phases/04-verify/` is empty but `03-execute/` has `SUMMARY.md` files | Set to Verify — `SUMMARY.md` is written by GSD's executor after each plan run; when GSD is not installed, use git log recency as the fallback signal |
| STATE.md `current_focus` is `02-plan` but `01-discuss/CONTEXT.md` is absent | Revert to Discuss |

**Session briefing output format — unchanged** except `Phase` now uses GSD vocabulary:
```
## Session briefing
Phase: Execute (03-execute)
Active task: [from .continue-here.md frontmatter: task N of total_tasks]
Effort remaining: ~N context window(s)
Pick up from: [<next_action> from .continue-here.md]

Budget for this session:
[phase-specific budget table from context-handover/phase-budgets.md]

Run /context-handover when approaching 80% usage.
```

### 5.3 `context-handover`

**Phase detection — updated priority order:**

1. Read `.harness/STATE.md` → `Current Position.Phase` field. Use if present.
2. Fallback: read active GitHub issue labels (`phase:discuss` / `phase:plan` / `phase:execute` / `phase:verify`).
3. Fallback: infer from task keywords.
4. Fallback: default to `execute`, note "phase inferred by default."

**Execution sequence:**

```
1. Invoke memory system (unchanged)

2. Update .harness/STATE.md
   → Session Continuity.Last session: [timestamp]
   → Session Continuity.Stopped at: [1-sentence summary]
   → Session Continuity.Resume file: .harness/phases/XX/.continue-here.md
   → Current Position.Status: [updated]
   → Current Position.Last activity: [date — what happened]
   Budget: <5% of remaining context

3. Write .harness/phases/XX-name/.continue-here.md
   → YAML frontmatter: phase, task, total_tasks, status, last_updated
   → XML sections: current_state, completed_work, remaining_work,
     decisions_made, blockers, context, next_action
   → Reference artifacts by path only — never inline content
   Budget: <5% of remaining context

4. Update GitHub issue (if docs/agents/ configured AND active task has an issue)
   → Unchanged from current spec

5. Output to user (unchanged)
   → "Handover complete. Resume file: .harness/phases/XX/.continue-here.md"
   → "Start next session with /session-start."
   → "To compact now, type /compact."
```

**Graceful degradation — updated:**
- No `.harness/` directory → note "run /setup-harness-skills first"; write `.claude/handoff.md` as emergency fallback only
- No `.continue-here.md` path resolvable → write to `.harness/phases/XX-current/.continue-here.md` using STATE.md `current_focus` value
- No GitHub remote → skip issue update silently (unchanged)

### 5.4 `to-prd`

**What it now produces:** `.harness/phases/01-discuss/01-CONTEXT.md` in GSD's 6-section CONTEXT.md format.

**Section mapping** (GSD section → this project's content):

| GSD section | Content |
|---|---|
| `<domain>` | Phase boundary — what the discuss phase delivers (from user's stated scope) |
| `<decisions>` | Implementation decisions — WHAT the system must respect (Technical Constraints in old spec) |
| `<canonical_refs>` | ADRs, spec sections, external docs cited during discussion |
| `<code_context>` | Brownfield: existing patterns, reusable assets, integration points |
| `<specifics>` | Specific user requirements ("I want it like X") |
| `<deferred>` | Ideas that came up but belong in other stages |

**What does NOT change:** The WHAT/HOW separation invariant. "Implementation Decisions" in the CONTEXT.md `<decisions>` section contains only WHAT (constraints), never HOW (file paths, class names, schemas). This maps cleanly to GSD's own CONTEXT.md spec: "Claude's Discretion" captures what the agent decides freely.

**After writing CONTEXT.md:** Note in the briefing: "CONTEXT.md written to `.harness/phases/01-discuss/01-CONTEXT.md`. Run `/gsd-plan-phase 1` (if GSD installed) or `/to-issues` to plan this stage."

### 5.5 `to-issues`

**Dual output when GitHub configured:**

1. **GitHub Issues** (unchanged) — for human visibility and HITL gate
2. **`.harness/phases/02-plan/02-PLAN.md`** (new) — GSD PLAN.md format tasks

GSD's PLAN.md format per task:
```markdown
## Task N: [title]

**Type:** feature | bug | chore | spike
**Effort:** N context window(s)

### What to build
[User-facing outcome, one sentence]

### Acceptance criteria
- [ ] [criterion]

### Files likely involved
[leave blank — agent decides HOW]
```

The existing BA user story format, confidence declaration, HITL/AFK routing, and three creation gates (estimable, ≤8 windows, vertical slice) all remain — they feed into the PLAN.md task content and the GitHub Issue body simultaneously.

### 5.6 `harness-engineering`

**Extended step 10 (installed skills detection):**

```
10. Check .harness/config.json:
    → Absent: no GSD-compatible setup — note in gaps list (optional: run /setup-harness-skills)
    → Present, no `harness` key: GSD is installed but harness skills not configured
      → After gaps, add: "GSD detected. Run /setup-harness-skills to configure GitHub integration."
    → Present, has `harness` key: full GSD-compatible setup
      → Mark "Already in place": GSD-compatible planning structure (.harness/)
```

**Extended ADR 0002 mapping table** (additions only):

| Gap | Closed by |
|---|---|
| `init.sh` absent | `/gsd health` (existing) |
| Judge audit (long-task exit criterion) | `/gsd-verify-work` (existing) |
| Session state (`.harness/STATE.md` present) | GSD-compatible setup via `/setup-harness-skills` or GSD |
| Handoff doc (`.harness/phases/XX/.continue-here.md` present) | `context-handover` |
| Project context (`.harness/PROJECT.md` present) | GSD-compatible setup |

**Stop hook remains gap #1** regardless of GSD presence. GSD does not write `.claude/settings.json`.

---

## 6. New ADR: 0003

`docs/adr/0003-gsd-file-structure-adoption.md`

```markdown
# ADR 0003: GSD File Structure Adoption

**Status:** Accepted

## Context

This collection used its own artifact locations (.claude/session.json, .claude/handoff.md,
.claude/harness.json) and its own phase vocabulary (Design/Product/Execution/Testing).
GSD Redux (open-gsd/get-shit-done-redux) uses .harness/STATE.md, .harness/phases/XX/,
and the verbs discuss/plan/execute/verify.

Users who adopt this collection and later install GSD face a migration. Users running both
simultaneously have two parallel session-state stores.

## Decision

This collection writes GSD-compatible artifacts from day one:
- .harness/STATE.md replaces .claude/session.json
- .harness/phases/XX/.continue-here.md replaces .claude/handoff.md
- .harness/config.json (harness namespace) replaces .claude/harness.json
- Phase vocabulary: discuss / plan / execute / verify

GSD ignores the `harness` namespace in config.json (unknown keys pass through).
When GSD is installed later, it reads the existing .harness/ artifacts directly.

## Consequences

- setup-harness-skills writes .harness/ in GSD format
- session-start reads STATE.md as the primary source
- context-handover writes .continue-here.md in GSD format
- to-prd creates .harness/phases/01-discuss/CONTEXT.md
- to-issues creates .harness/phases/02-plan/PLAN.md + GitHub Issues
- harness-engineering extends the ADR 0002 gap mapping for .harness/ detection
- All skill evals updated: fixture scaffolds use .harness/ paths
- Old .claude/ artifacts (session.json, handoff.md, harness.json) are deprecated;
  setup-harness-skills migrates existing values on re-run
```

---

## 7. Evals Impact

**Evals requiring updates (path/fixture only — no scenario changes):**

| Skill | Eval IDs | Change |
|---|---|---|
| `context-handover` | 1, 2, 3 | Scaffold: `session_json` → `state_md`; expected path: `handoff.md` → `.continue-here.md`; phase names |
| `session-start` | 1, 2, 3 | Scaffold: `session_json` → `state_md`, `handoff_doc` → `.continue-here.md` path; phase names |
| `harness-engineering` | 7, 8 | Scaffold: add `planning_config_json` flag; expected text updates |
| `to-prd` | all | Expected output path changes from `docs/superpowers/specs/*.md` to `.harness/phases/01-discuss/CONTEXT.md` |
| `to-issues` | all | Expected output: now includes both `.harness/phases/02-plan/PLAN.md` and GitHub Issues |

**New evals needed:**

| Skill | Scenario |
|---|---|
| `setup-harness-skills` | GSD already installed (`.harness/config.json` exists without `harness` key) — should configure harness namespace, not overwrite GSD config |
| `session-start` | `.harness/STATE.md` exists with `current_focus: 02-plan` and `.continue-here.md` present — should brief from these files |
| `harness-engineering` | `.harness/config.json` with `harness` key present — "GSD-compatible setup" in Already in Place |

---

## 8. Migration for Existing Users

Users with existing `.claude/session.json`, `.claude/handoff.md`, or `.claude/harness.json`:

`setup-harness-skills` on re-run detects old files and migrates:
1. Reads `.claude/harness.json` → writes values into `.harness/config.json` harness namespace (merge, not overwrite)
2. Reads `.claude/session.json` → writes Session Continuity section of `.harness/STATE.md`
3. Reads `.claude/handoff.md` → best-effort mapping into `.continue-here.md`: known sections map to their equivalent XML section; any remaining content is preserved verbatim in `<context>`. Migration is intentionally lossy — `.continue-here.md` uses GSD's schema going forward.
4. Appends old files to `.gitignore` so they stop being committed if they were tracked

Old files are NOT deleted — user confirms before removal.

---

## 9. Implementation Order

| Phase | What | Rationale |
|---|---|---|
| 1 | ADR 0003 | Governance document first — all subsequent changes reference it |
| 2 | Phase vocabulary rename | Find-replace across all SKILLs + evals; low risk, establishes terminology for phases 3-5 |
| 3 | `setup-harness-skills` | Gateway — creates the .harness/ structure everything else reads |
| 4 | `context-handover` | Writes the artifacts session-start depends on |
| 5 | `session-start` | Reads the artifacts context-handover writes |
| 6 | `to-prd` + `to-issues` | Dual output; depends on .harness/phases/ directory existing |
| 7 | `harness-engineering` | Extended detection; lowest dependency |
| 8 | Evals | Update after skills are stable |

---

## 10. Out of Scope

- GSD's parallel wave execution (worktrees) — this collection has no execution engine
- GSD's 15-runtime installer — this collection targets Claude Code only
- GSD's knowledge graph (graphify) — domain-specific tool, not a harness concern
- GSD's research agent — no equivalent in this collection; `/gsd-plan-phase` handles it
- Automated GSD installation — users install GSD separately; this collection only writes compatible artifacts
