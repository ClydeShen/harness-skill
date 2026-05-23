# Harness Engineering Skill Collection — Design Spec

**Date:** 2026-05-24
**Status:** Approved
**Scope:** Full repo refactor — single skill → curated skill collection

---

## 1. Problem Statement

The current repo ships one skill (`harness-engineering`) that detects harness gaps and outputs paste-ready snippets. It solves setup, not lifecycle. Users still lack:

- An onboarding skill that configures the whole tool chain once per project
- A way to manage long-running agent tasks through GitHub Projects
- Context window discipline across multi-session work (handover, phase budgets, session state)

This spec defines a refactor into a complete skill collection modeled on `mattpocock/skills`, with three new skills and one new hook script.

---

## 2. Design Principles

| Principle | Application |
|---|---|
| **Minimal fork** | Adapted mattpocock skills change at most one sentence. Content is never duplicated. |
| **Gateway pattern** | `setup-harness-skills` runs once per project and writes all config that other skills read. |
| **Graceful degradation** | Every skill works without `docs/agents/` config — it just asks instead of reading. |
| **YAGNI** | No abstract phase-routing engine. Phase detection is a few `if` conditions in the skill. |
| **One level deep** | Reference files link directly from SKILL.md, never nested. |

---

## 3. Repo Structure

```
harness-engineering-skill/
├── .claude-plugin/
│   ├── plugin.json              ← registered skill list (mirrors mattpocock format)
│   └── link-skills.sh           ← symlinks skills/ into ~/.claude/skills/
├── skills/
│   ├── engineering/
│   │   ├── README.md
│   │   ├── setup-harness-skills/        ← NEW (gateway — run first)
│   │   │   ├── SKILL.md
│   │   │   ├── issue-tracker-github.md  ← seed template
│   │   │   ├── issue-tracker-github-projects.md  ← seed template
│   │   │   ├── triage-labels.md         ← seed template
│   │   │   ├── domain.md                ← seed template
│   │   │   ├── github-project.md        ← seed template
│   │   │   └── session-config.md        ← seed template
│   │   ├── harness-engineering/         ← EXISTING (enhanced — reads docs/agents/)
│   │   │   ├── SKILL.md
│   │   │   ├── skill.json
│   │   │   ├── evals/
│   │   │   │   └── evals.json
│   │   │   └── references/
│   │   │       ├── detect.md
│   │   │       ├── universal-snippets.md
│   │   │       ├── node-snippets.md
│   │   │       ├── python-snippets.md
│   │   │       └── kiro-snippets.md
│   │   ├── context-handover/            ← NEW (core differentiator)
│   │   │   ├── SKILL.md
│   │   │   └── phase-budgets.md
│   │   ├── session-start/               ← NEW (phase detection + briefing)
│   │   │   └── SKILL.md
│   │   ├── triage/                      ← ADAPTED (one-line change)
│   │   │   └── SKILL.md
│   │   ├── to-prd/                      ← ADAPTED (one-line change)
│   │   │   └── SKILL.md
│   │   ├── to-issues/                   ← ADAPTED (one-line change)
│   │   │   └── SKILL.md
│   │   └── zoom-out/                    ← COPIED (zero changes)
│   │       └── SKILL.md
│   └── productivity/
│       ├── caveman/                     ← COPIED (zero changes)
│       ├── grill-me/                    ← COPIED (zero changes)
│       ├── handoff/                     ← COPIED (zero changes)
│       └── write-a-skill/              ← ADAPTED (add harness checklist item)
│           └── SKILL.md
├── hooks/
│   └── context-monitor.sh              ← NEW: PostToolUse hook
├── scripts/
│   ├── link-skills.sh
│   └── list-skills.sh
├── evals/
│   └── run_evals.py                    ← EXISTING (enhanced for multi-skill)
├── CLAUDE.md
├── CONTEXT.md
└── README.md
```

---

## 4. Skills Inventory

### Skills carried from mattpocock/skills

| Skill | Type | Change |
|---|---|---|
| `zoom-out` | Engineering | None — copied verbatim |
| `caveman` | Productivity | None — copied verbatim |
| `grill-me` | Productivity | None — copied verbatim |
| `handoff` | Productivity | None — copied verbatim |
| `triage` | Engineering | Replace `setup-matt-pocock-skills` reference → `setup-harness-skills` |
| `to-prd` | Engineering | Replace `setup-matt-pocock-skills` reference → `setup-harness-skills` |
| `to-issues` | Engineering | Replace `setup-matt-pocock-skills` reference → `setup-harness-skills` |
| `write-a-skill` | Productivity | Add one checklist item: "Does the skill note its typical context window cost?" |

### Skills NOT included (out of scope for this collection)

`prototype`, `tdd`, `improve-codebase-architecture`, `grill-with-docs`, `diagnose` — engineering skills too domain-specific for a harness-focused collection. Users install `mattpocock/skills` separately for these.

### New skills (designed in this spec)

1. `setup-harness-skills` — gateway
2. `context-handover` — core differentiator
3. `session-start` — phase detection + briefing

---

## 5. Skill Designs

### 5.1 `setup-harness-skills` (Gateway)

**YAML frontmatter:**
```yaml
name: setup-harness-skills
description: >
  Sets up an ## Agent skills block in AGENTS.md/CLAUDE.md and docs/agents/ so
  harness skills know the issue tracker, triage labels, domain docs, GitHub
  Project board, and session state location. Run before first use of triage,
  to-prd, to-issues, context-handover, or session-start — or if those skills
  appear to be missing context.
disable-model-invocation: true
```

**Interaction flow (one section at a time, never dump all at once):**

**Section A — Issue tracker**
> Explainer: Where do issues live? Skills like `triage`, `to-prd`, `to-issues` read from and write to it.
- GitHub Issues (uses `gh` CLI)
- GitHub Projects v2 (uses GraphQL API)
- Local markdown (`.scratch/<feature>/`)
- Other (user describes in prose)

**Section B — Triage label vocabulary**
> Explainer: Five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Override if your repo uses different strings.

**Section C — Domain docs**
> Explainer: Single-context (one CONTEXT.md + docs/adr/) or multi-context (CONTEXT-MAP.md for monorepos)?

**Section D — GitHub Project board** *(new, not in mattpocock/skills)*
> Explainer: The `context-handover` and `session-start` skills track long-running tasks on a GitHub Project board. Which board? What are your column names for Backlog / In Progress / Done?

**Section E — Session state location** *(new)*
> Explainer: `.claude/session.json` tracks the active phase and task across sessions. Confirm this location or override it.

**Output after all five sections:**

1. Confirm draft of `## Agent skills` block with user before writing
2. Write block to whichever of CLAUDE.md / AGENTS.md exists (never create the other)
3. Write seed files to `docs/agents/`:
   - `issue-tracker.md` — from bundled template per tracker type
   - `triage-labels.md` — from bundled template
   - `domain.md` — from bundled template
   - `github-project.md` — from bundled template *(new)*
   - `session-config.md` — from bundled template *(new)*

**Bundled seed templates** (inside `setup-harness-skills/` skill folder):
- `issue-tracker-github.md`
- `issue-tracker-github-projects.md`
- `triage-labels.md`
- `domain.md`
- `github-project.md` — default columns: `Backlog`, `In Progress`, `Done`; default effort field: `Effort (windows)`
- `session-config.md` — session.json schema documentation

---

### 5.2 `context-handover`

**YAML frontmatter:**
```yaml
name: context-handover
description: >
  Save memory, write a handoff document, update the active GitHub issue, and
  compact the context window so a fresh session can resume seamlessly. Invoked
  automatically by the context-monitor hook at 80% usage, or manually with
  /context-handover [next-session-focus].
argument-hint: "What will the next session focus on?"
```

**Phase detection (in priority order):**
1. Read `.claude/session.json` → `current_phase`
2. If absent: read active GitHub issue labels — label `phase:design / phase:product / phase:execution / phase:testing` maps to phase
3. If no label: read issue title/body, infer from task type (e.g. "write PRD" → product, "implement" → execution)
4. If still unknown: default to `execution`, note uncertainty in handoff doc

**Execution sequence:**

```
1. Save memory
   → Invoke memobank skill if installed
   → Write key decisions to MEMORY.md if memobank absent
   Budget: <5% of remaining context

2. Write handoff doc
   → Path: $TEMP/harness-handoff-YYYY-MM-DD-HHmm.md
   → Content per phase (see phase-budgets.md):
      Design: decisions made, open questions, next doc to write
      Product: stories broken down, next story, effort remaining
      Execution: code written, test status, next file/function
      Testing: issues found, root causes, next test case
   → Reference artifacts by path/URL only — never inline content
   → Include "Suggested skills" section
   Budget: <5% of remaining context

3. Update GitHub issue (if docs/agents/issue-tracker.md exists)
   → Add comment: status summary + next step
   → Update session.json: last_handover, next_session_hint

4. Output to user
   → "Handover complete. Handoff doc: [path]. Next session: /session-start"
   → Trigger /compact
```

**Reference file:** `phase-budgets.md` — defines what each phase's handoff focuses on. Kept separate from SKILL.md to stay under 500-line limit.

---

### 5.3 `session-start`

**YAML frontmatter:**
```yaml
name: session-start
description: >
  Brief the current session: reads session state, handoff doc, and memory to
  determine the active phase, task, and context budget. Outputs a structured
  briefing. Use at the start of every long-running agent session.
```

**Execution sequence:**

```
1. Read .claude/session.json (if exists) → phase, active task, effort estimate
2. Read most recent $TEMP/harness-handoff-*.md (glob, sort by mtime)
3. Read MEMORY.md or top-3 memobank entries relevant to active task
4. If session.json absent: infer phase from GitHub issue state + labels
5. Output structured briefing:
   ---
   ## Session briefing
   Phase: [Design / Product / Execution / Testing]
   Active task: #[N] — [title]
   Effort remaining: ~[N] context window(s)
   Pick up from: [specific next step from handoff doc]

   Budget for this session:
   [phase-specific budget table]

   Run /context-handover when approaching 80% usage.
   ---
```

**Phase budget tables** (from `references/phase-budgets.md` in context-handover):

| Phase | Reading | User/Agent dialogue | Main output | Review | Memory | Handover |
|---|---|---|---|---|---|---|
| Design | <10% | <20% | <40% | <10% | <5% | <5% |
| Product | <20% | — | <40% | <10% | <5% | <5% |
| Execution | <20% | — | <40% | <10% | <5% | <5% |
| Testing | <20% | — | <40% | <20% | <5% | <5% |

---

### 5.4 Hook: `context-monitor.sh`

Registered as `PostToolUse` hook in `.claude/settings.json` (written by `setup-harness-skills`).

```bash
#!/bin/bash
# Reads context usage from Claude's environment.
# Fires after every tool use.

USAGE_PCT=${CLAUDE_CONTEXT_USAGE_PCT:-0}

if [ "$USAGE_PCT" -ge 95 ]; then
  echo "CRITICAL: Context at ${USAGE_PCT}%. Run /context-handover immediately before continuing any work."
elif [ "$USAGE_PCT" -ge 80 ]; then
  echo "WARNING: Context at ${USAGE_PCT}%. Run /context-handover before starting the next task."
fi
```

**Note:** `$CLAUDE_CONTEXT_USAGE_PCT` is the env var name to verify against Claude's hook documentation at implementation time. If unavailable, the hook reads token counts from the hook event payload.

---

### 5.5 `.claude/session.json` Schema

```json
{
  "schema_version": 1,
  "current_phase": "execution",
  "active_task": {
    "github_issue": 42,
    "title": "Implement context-monitor.sh hook",
    "effort_estimate": 1,
    "github_project_item_id": "PVI_xxxx"
  },
  "context_budget_used_pct": 45,
  "last_handover": "2026-05-24T10:30:00Z",
  "next_session_hint": "Continue from writing context-monitor.sh — bash conditional logic done, need to test with real token env var"
}
```

Written by: `session-start` (initializes), `context-handover` (updates).
Read by: `context-monitor.sh` hook, `session-start`, `context-handover`, `harness-engineering`.

---

## 6. Enhanced `harness-engineering` Skill

One addition to Phase 1 detection (step after runtime detection):

> Check `docs/agents/` — if present: note `setup-harness-skills` has been run and load context. If absent: after gap analysis, add: *"Consider running `/setup-harness-skills` to configure the full harness toolchain for this project."*

This means `harness-engineering` degrades gracefully — it still works without `docs/agents/`, but rewards users who've run the onboarding.

---

## 7. Skill Writing Conventions

All skills in this collection follow these rules (derived from Anthropic best practices + mattpocock/skills patterns):

1. **YAML frontmatter:** `name` (lowercase/hyphens, ≤64 chars), `description` (third person, ≤1024 chars, includes "use when" trigger), optional `argument-hint`, optional `disable-model-invocation: true`
2. **SKILL.md body:** ≤500 lines. Long content moves to reference files.
3. **Reference files:** One level deep from SKILL.md only. Never nested.
4. **Cross-skill awareness:** Every skill that needs setup config says: *"run `/setup-harness-skills` if missing context"*
5. **No time-sensitive content:** No dates in skill bodies. Use "old patterns" section for deprecated approaches.
6. **Consistent terminology:** One term per concept across all files.
7. **Forward slashes only** in all file paths.
8. **Context cost note** (new, not in mattpocock): Each skill's description mentions typical context window cost — e.g., "typically consumes <5% of a context window".

---

## 8. Eval Strategy

### Per-skill evals (minimum 3 each)

**`setup-harness-skills`**
1. Happy path: runs setup on fresh repo, writes all 5 `docs/agents/` files, adds `## Agent skills` block to CLAUDE.md
2. Existing config: partial `docs/agents/` present — updates in-place, does not overwrite user edits
3. No instruction file: neither CLAUDE.md nor AGENTS.md exists — asks user which to create

**`context-handover`**
1. Happy path: 80% usage signal, phase inferred from session.json, handoff doc written, GitHub issue updated
2. No session state: session.json absent — phase inferred from issue labels, handoff still written
3. Handoff references: handoff doc uses issue URL + artifact paths, never inlines content

**`session-start`**
1. Happy path: reads session.json + handoff doc, outputs correct phase briefing with budget table
2. Fresh session: no prior session.json or handoff doc — graceful output, infers from GitHub issue
3. Phase inference: no session.json, issue has `phase:product` label — correctly outputs Product briefing

**`harness-engineering` (enhanced)**
1. Existing: `docs/agents/` present — notes setup already run, uses config in gap analysis
2. Not set up: no `docs/agents/` — normal gap analysis + suggests running `/setup-harness-skills`

### Eval runner enhancement

`run_evals.py` currently runs 6 evals for one skill. Enhance to:
- Accept `--skill <name>` flag to run evals for a specific skill
- Default (no flag): run all skills' evals
- Results grouped by skill in output

---

## 9. Implementation Order

| Phase | What | Why |
|---|---|---|
| 1 | Repo restructure | Clean foundation — move files, create `.claude-plugin/`, update `plugin.json` |
| 2 | `setup-harness-skills` | Gateway — needed by everything else |
| 3 | `context-handover` + `session-start` + `context-monitor.sh` | Core new value |
| 4 | Adapt mattpocock skills | Low-effort: one-line change each |
| 5 | Enhance `harness-engineering` | Read `docs/agents/` config |
| 6 | Eval runner + new evals | Verify all skills pass |

Each phase is one implementation plan / spec cycle.

---

## 10. Out of Scope

- `prototype`, `tdd`, `improve-codebase-architecture`, `grill-with-docs`, `diagnose` (use mattpocock/skills)
- Multi-agent orchestration beyond subagent spawning
- Non-GitHub issue trackers in the initial version (noted in Section D as extensible)
- Windows-specific hook scripts (hooks/ targets bash; Windows users use WSL)
