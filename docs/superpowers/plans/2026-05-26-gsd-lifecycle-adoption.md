# GSD Lifecycle Adoption — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the harness-engineering skill collection with GSD Redux artifact structure so projects using this collection produce GSD-compatible files natively, while enriching GSD's lifecycle with context-handover, session-start state machine, grill-with-docs integration, and system-agnostic memory detection.

**Architecture:** Skills write to `.harness/` in GSD-compatible format (STATE.md, .continue-here.md, config.json harness namespace, phases/ directories). `session-start` gains a write step that initiates a state machine (`session_status: in_progress`); `context-handover` closes it (`session_status: idle`). Interrupted sessions are detected by the next `session-start` reading a stale `in_progress` timestamp.

**Tech Stack:** Markdown SKILL.md files, YAML promptfoo eval configs, Python scaffold_helper.py, ADR markdown docs.

**Prerequisite:** A llamacpp server must be running at `localhost:8080` to run evals. All eval commands below assume `cd evals/promptfoo` first.

**Spec:** `docs/superpowers/specs/2026-05-26-gsd-lifecycle-adoption-design.md`
**ADR (state machine, already written):** `docs/adr/0004-state-machine-in-state-md.md`

---

## Chunk 1: Foundation — ADR 0003 + Vocabulary Rename

### Task 1: Write ADR 0003

**Files:**
- Create: `docs/adr/0003-gsd-file-structure-adoption.md`

- [ ] **Step 1: Create the ADR**

Write `docs/adr/0003-gsd-file-structure-adoption.md` with this exact content:

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
- session-start reads STATE.md as the primary source and writes session_status on begin
- context-handover writes .continue-here.md in GSD format and session_status: idle on exit
- to-prd creates .harness/phases/01-discuss/CONTEXT.md
- to-issues creates .harness/phases/02-plan/PLAN.md + GitHub Issues
- harness-engineering extends gap detection for .harness/ and memory systems
- All skill evals updated: fixture scaffolds use .harness/ paths
- Old .claude/ artifacts (session.json, handoff.md, harness.json) are deprecated;
  setup-harness-skills migrates existing values on re-run
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0003-gsd-file-structure-adoption.md
git commit -m "docs(adr): add ADR 0003 GSD file structure adoption"
```

---

### Task 2: Vocabulary Rename — CONTEXT.md

**Files:**
- Modify: `CONTEXT.md`

The full rename: Design→discuss, Product→plan, Execution→execute, Testing→verify (as phase names). Capital initial is preserved where used as a proper noun in headings; lowercase in running text.

- [ ] **Step 1: Locate all phase-name occurrences in CONTEXT.md**

```bash
grep -n "Design\|Product\|Execution\|Testing" CONTEXT.md | grep -i "phase\|stage"
```

Expected: ~25 matches across `### Project Phase`, `### Phase Exit Criteria`, `### Task (Session Task)`, `### User Story`, `### Spike`, `### HITL / AFK`, `### Context Handover`.

- [ ] **Step 2: Update `### Project Phase` definition**

Find:
```
### Project Phase
One of four project-level phases: Design, Product, Execution, Testing. The default order is Design → Product → Execution → Testing
```

Replace with:
```
### Project Phase
One of four project-level phases: discuss, plan, execute, verify. The default order is discuss → plan → execute → verify
```

Apply the same substitution to the skip/revert table within that section:
- "Skip Design" → "Skip discuss"
- "Skip Design + Product" → "Skip discuss + plan"
- "Revert to Design" → "Revert to discuss"
- "Revert to Product" → "Revert to plan"
- `current_phase == "product"` → `current_phase == "plan"`
- `current_phase == "execution"` → `current_phase == "execute"`

- [ ] **Step 3: Update `### Phase Exit Criteria`**

Replace all four per-phase oracle labels:
- "**Design**:" → "**discuss**:"
- "**Product**:" → "**plan**:"
- "**Execution**:" → "**execute**:"
- "**Testing**:" → "**verify**:"

Update the spec reference: "Defined during Design phase for all phases" → "Defined during discuss phase for all phases"

- [ ] **Step 4: Update `### Task (Session Task)` task-anchor table**

Replace:
```
- **Design phase**: the Design Phase Tracking Issue
- **Product phase**: one PRD document
- **Execution phase**: one GitHub issue number
- **Testing phase**: one test plan document
```
With:
```
- **discuss phase**: the Discuss Phase Tracking Issue
- **plan phase**: one PRD document
- **execute phase**: one GitHub issue number
- **verify phase**: one test plan document
```

- [ ] **Step 5: Update `### Context Handover` per-phase trigger points**

Replace:
```
Per-phase trigger points: Design ≥70% used, Product ≥70% used, Execution ≥70% used.
```
With:
```
Per-phase trigger points: discuss ≥70% used, plan ≥70% used, execute ≥70% used.
```

- [ ] **Step 6: Update deprecated artifact terms**

In `### session.json`, add a deprecation note at the top:
```
> **Deprecated.** Replaced by `.harness/STATE.md` (GSD-compatible). See ADR 0003.
> setup-harness-skills migrates existing values on re-run.
```

In `### handoff.md`, add:
```
> **Deprecated.** Replaced by `.harness/phases/XX/.continue-here.md` (GSD format). See ADR 0003.
```

In `### harness.json`, add:
```
> **Deprecated.** Replaced by `.harness/config.json` with `harness` namespace. See ADR 0003.
```

- [ ] **Step 7: Update remaining scattered occurrences**

Find and replace in CONTEXT.md:
- "Execution phase agent" → "execute phase agent"
- "Execution phase issues" → "execute phase issues"
- "phase:execution" → "phase:execute" (label values)
- "phase:design" → "phase:discuss"
- "phase:product" → "phase:plan"
- "phase:testing" → "phase:verify"
- "Design Phase Tracking Issue" → "Discuss Phase Tracking Issue"
- "design-approved" label → "discuss-approved"

- [ ] **Step 8: Verify no missed occurrences**

```bash
grep -n "\bDesign phase\b\|\bProduct phase\b\|\bExecution phase\b\|\bTesting phase\b" CONTEXT.md
```

Expected: 0 matches (all renamed).

- [ ] **Step 9: Commit**

```bash
git add CONTEXT.md
git commit -m "refactor: rename phase vocabulary Design/Product/Execution/Testing → discuss/plan/execute/verify in CONTEXT.md"
```

---

### Task 3: Vocabulary Rename — SKILL.md Files

**Files:**
- Modify: `skills/engineering/session-start/SKILL.md`
- Modify: `skills/engineering/context-handover/SKILL.md`
- Modify: `skills/engineering/harness-engineering/SKILL.md`
- Modify: `skills/engineering/to-prd/SKILL.md`
- Modify: `skills/engineering/to-issues/SKILL.md`
- Modify: `skills/engineering/setup-harness-skills/SKILL.md`

- [ ] **Step 1: Grep for old phase names across all skill files**

```bash
grep -rn "Design\|Product\|Execution\|Testing" skills/ --include="*.md" | grep -i "phase\|stage"
```

- [ ] **Step 2: Update session-start SKILL.md output format**

Find:
```
Phase: [Design / Product / Execution / Testing]
```
Replace:
```
Phase: [discuss / plan / execute / verify]
```

Find the phase skip/revert table and replace:
- "Skip Design → set phase to Product" → "Skip discuss → set phase to plan"
- "Skip Design + Product → set phase to Execution" → "Skip discuss + plan → set phase to execute"
- "Revert to Design" → "Revert to discuss"
- "Revert to Product" → "Revert to plan"

- [ ] **Step 3: Update context-handover SKILL.md phase label fallback chain**

Find:
```
phase:design / product / execution / testing
```
Replace:
```
phase:discuss / plan / execute / verify
```

Find fallback keywords:
```
"design"/"spec"/"ADR" → design; "PRD"/"story" → product; "implement"/"build"/"fix" → execution; "test"/"QA" → testing
```
Replace:
```
"design"/"spec"/"ADR" → discuss; "PRD"/"story" → plan; "implement"/"build"/"fix" → execute; "test"/"QA" → verify
```

- [ ] **Step 4: Apply same substitution to all other SKILL.md files found in Step 1**

- [ ] **Step 5: Commit**

```bash
git add skills/
git commit -m "refactor: rename phase vocabulary in all SKILL.md files"
```

---

## Chunk 2: Gateway — scaffold_helper.py + setup-harness-skills

### Task 4: Add .harness/ Scaffold Patterns to scaffold_helper.py

**Files:**
- Modify: `evals/promptfoo/scaffold_helper.py`

These patterns are needed by every subsequent eval that tests GSD-compatible behavior.

- [ ] **Step 1: Add STATE.md scaffold handler**

After the `.claude/handoff.md` block (line ~321), add:

```python
# .harness/STATE.md — idle state (clean prior session)
if "state.md" in desc and "idle" in desc:
    planning = root / ".harness"
    planning.mkdir(exist_ok=True)
    import re
    phase_match = re.search(r"current[_ ]focus[:\s]+(\S+)", desc)
    phase = phase_match.group(1) if phase_match else "02-plan"
    task_match = re.search(r"issue (\d+)", desc)
    task_num = task_match.group(1) if task_match else "42"
    (planning / "STATE.md").write_text(textwrap.dedent(f"""\
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

        **Core value:** Harness engineering skill collection
        **Current focus:** {phase}

        ## Current Position

        Phase: 2 of 4 ({phase})
        Status: In progress
        Last activity: 2026-05-26 — context handover

        ## Session Continuity

        session_status: idle
        session_started:
        last_session: 2026-05-26 14:30
        Stopped at: Finished auth middleware, starting route handlers next.
        Resume file: .harness/phases/{phase}/.continue-here.md
    """))

# .harness/STATE.md — in_progress with stale timestamp (interrupted session)
if "state.md" in desc and "interrupted" in desc:
    planning = root / ".harness"
    planning.mkdir(exist_ok=True)
    import re
    task_match = re.search(r"issue (\d+)", desc)
    task_num = task_match.group(1) if task_match else "42"
    (planning / "STATE.md").write_text(textwrap.dedent(f"""\
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

        **Core value:** Harness engineering skill collection
        **Current focus:** 03-execute

        ## Current Position

        Phase: 3 of 4 (03-execute)
        Active task: #{task_num}
        Status: In progress
        Last activity: 2026-05-25 — session started

        ## Session Continuity

        session_status: in_progress
        session_started: 2026-05-25T10:15:00Z
        last_session: 2026-05-24 18:00
        Stopped at: Writing auth middleware tests.
        Resume file: .harness/phases/03-execute/.continue-here.md
    """))
```

- [ ] **Step 2: Add .continue-here.md scaffold handler**

```python
# .harness/phases/XX/.continue-here.md
if ".continue-here.md" in desc or "continue-here" in desc:
    import re
    phase_match = re.search(r"phase[:\s]+(\S+)", desc)
    phase = phase_match.group(1) if phase_match else "03-execute"
    phase_dir = root / ".harness" / "phases" / phase
    phase_dir.mkdir(parents=True, exist_ok=True)
    (planning_dir := root / ".harness").mkdir(exist_ok=True)
    task_match = re.search(r"task (\d+)", desc)
    total_match = re.search(r"total[_ ]tasks (\d+)", desc)
    task_num = task_match.group(1) if task_match else "2"
    total = total_match.group(1) if total_match else "5"
    (phase_dir / ".continue-here.md").write_text(textwrap.dedent(f"""\
        ---
        phase: {phase}
        task: {task_num}
        total_tasks: {total}
        status: in_progress
        last_updated: 2026-05-26T14:30:00Z
        ---

        <current_state>
        Implementing auth middleware for issue #42.
        </current_state>

        <completed_work>
        - Task 1: Schema migration — Done
        - Task 2: Auth middleware stub — Done
        </completed_work>

        <remaining_work>
        - Task 2: Wire middleware into Express routes
        - Task 3: Write integration tests
        </remaining_work>

        <decisions_made>
        - Used JWT over session cookies for stateless auth
        </decisions_made>

        <blockers>
        None
        </blockers>

        <context>
        Middleware stub is in src/auth/middleware.ts. Routes in src/routes/.
        </context>

        <next_action>
        Start with: Wire auth middleware into src/routes/index.ts
        </next_action>
    """))
```

- [ ] **Step 3: Add .harness/config.json scaffold handler**

```python
# .harness/config.json
if "planning config" in desc or "planning/config" in desc:
    planning = root / ".harness"
    planning.mkdir(exist_ok=True)
    has_harness = "harness key" in desc or "with harness" in desc
    config: dict = {
        "model_profile": "balanced",
        "commit_docs": True,
    }
    if has_harness:
        config["harness"] = {
            "schema_version": 1,
            "github": {
                "owner": "org",
                "repo": "my-project",
                "default_branch": "main",
            },
            "docs_agents_dir": "docs/agents",
            "issue_tracker": "github",
        }
    (planning / "config.json").write_text(json.dumps(config, indent=2))
```

- [ ] **Step 4: Verify scaffold_helper.py is importable**

```bash
cd evals/promptfoo && python -c "from scaffold_helper import scaffold; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add evals/promptfoo/scaffold_helper.py
git commit -m "feat(evals): add .harness/ scaffold patterns for STATE.md, .continue-here.md, config.json"
```

---

### Task 5: Update setup-harness-skills SKILL.md

**Files:**
- Modify: `skills/engineering/setup-harness-skills/SKILL.md`

- [ ] **Step 1: Update Step 1 — Explore (add .harness/ reads)**

Find the Step 1 explore list:
```
1. `.git/config` → remote origin (owner/repo)
2. `CLAUDE.md` / `AGENTS.md` → existing `## Agent skills` block?
3. `CONTEXT.md` → present?
4. `docs/agents/` → prior setup files?
5. `.claude/harness.json` → prior config?
```

Replace with:
```
1. `.git/config` → remote origin (owner/repo)
2. `CLAUDE.md` / `AGENTS.md` → existing `## Agent skills` block?
3. `CONTEXT.md` → present?
4. `docs/agents/` → prior setup files?
5. `.harness/config.json` → prior GSD or harness setup? (read harness key if present)
6. `.harness/STATE.md` → prior session state?
7. `.harness/PROJECT.md` → prior project context?
8. `.claude/harness.json` → old config to migrate? (deprecated — migrate values to .harness/config.json)
```

- [ ] **Step 2: Update Section E — Session State**

Find:
```
## Section E — Session State Location

> "`.claude/session.json` tracks active phase and task. Confirm this path or override?"
```

Replace:
```
## Section E — Session State Location

> "`.harness/STATE.md` tracks active phase, session status, and last-session context. This follows GSD's format — install GSD at any time and it reads this file directly. Confirm this path or override?"
```

- [ ] **Step 3: Update Output section**

Find the output description and add the .harness/ file creation steps:

After "After all five sections, show the draft of what will be written and confirm before writing." add:

```
### .harness/ files written by setup-harness-skills

1. `.harness/config.json` — GSD defaults + `harness` namespace (idempotent merge; never overwrites GSD keys)
2. `.harness/STATE.md` — from GSD state template (only if absent)
3. `.harness/PROJECT.md` — from GSD project template (only if absent)
4. `.harness/ROADMAP.md` — stub with four phase entries: 01-discuss, 02-plan, 03-execute, 04-verify (only if absent)

### .gitignore additions

```
.harness/phases/*/.continue-here.md   # handoff docs — ephemeral, never commit
```

### Migration (when old .claude/ artifacts exist)

- `.claude/harness.json` → merge values into `.harness/config.json` harness namespace
- `.claude/session.json` → copy Session Continuity values into `.harness/STATE.md`
- `.claude/handoff.md` → map into `.continue-here.md` XML sections (lossy — preserves content in `<context>`)
- Old files are NOT deleted — user confirms before removal
```

- [ ] **Step 4: Run eval to verify no regression**

```bash
cd evals/promptfoo && promptfoo eval --config setup-harness-skills.yaml --no-cache
```

Expected: all existing evals pass.

- [ ] **Step 5: Commit**

```bash
git add skills/engineering/setup-harness-skills/SKILL.md
git commit -m "feat(setup-harness-skills): migrate to .harness/ structure, GSD-compatible artifacts"
```

---

## Chunk 3: Writer — context-handover

### Task 6: Update context-handover SKILL.md

**Files:**
- Modify: `skills/engineering/context-handover/SKILL.md`

- [ ] **Step 1: Update phase detection priority order**

Find:
```
1. `.claude/session.json` → `current_phase` — use if present and non-null
2. Active GitHub issue labels → `phase:design / product / execution / testing`
3. Issue title/body keywords — "design"/"spec"/"ADR" → design; "PRD"/"story" → product; "implement"/"build"/"fix" → execution; "test"/"QA" → testing
4. Default to `execution` — note "phase inferred by default" in handoff doc
```

Replace:
```
1. `.harness/STATE.md` → `Current Position.Phase` field — use if present
2. `.claude/session.json` → `current_phase` — legacy fallback (deprecated)
3. Active GitHub issue labels → `phase:discuss / plan / execute / verify`
4. Issue title/body keywords — "design"/"spec"/"ADR" → discuss; "PRD"/"story" → plan; "implement"/"build"/"fix" → execute; "test"/"QA" → verify
5. Default to `execute` — note "phase inferred by default" in handoff doc
```

- [ ] **Step 2: Update execution sequence — write step**

Find:
```
- [ ] **2. Write `.claude/handoff.md`** — overwrite in place (single unified file, no timestamps in path). See `phase-budgets.md` for what each phase's handoff focuses on. Rules:
  - Reference artifacts by path/URL only — never inline file contents
  - Include a "Suggested skills" section
  - Always include `Last updated: YYYY-MM-DD HH:mm` at the top
  - Budget: <5% of remaining context
```

Replace:
```
- [ ] **2. Update `.harness/STATE.md` Session Continuity** — write `session_status: idle`, `last_session`, `Stopped at`, `Resume file` fields. Budget: <1% of remaining context.

- [ ] **3. Write `.harness/phases/XX-name/.continue-here.md`** — use GSD's exact template. Path: derive XX-name from STATE.md `Current Position.Phase`. Rules:
  - YAML frontmatter: phase, task, total_tasks, status, last_updated
  - XML sections: current_state, completed_work, remaining_work, decisions_made, blockers, context, next_action
  - Reference artifacts by path only — never inline content
  - Budget: <5% of remaining context

  Template:
  ```
  ---
  phase: 03-execute
  task: 2
  total_tasks: 5
  status: in_progress
  last_updated: YYYY-MM-DDTHH:MM:SSZ
  ---

  <current_state>
  Where exactly are we?
  </current_state>

  <completed_work>
  - Task 1: [name] — Done
  </completed_work>

  <remaining_work>
  - Task 2: [what's left]
  </remaining_work>

  <decisions_made>
  - Decided to use X because Y
  </decisions_made>

  <blockers>
  None
  </blockers>

  <context>
  Mental state and vibe to resume smoothly.
  </context>

  <next_action>
  Start with: [specific action]
  </next_action>
  ```
```

- [ ] **Step 3: Renumber steps — GitHub comment becomes step 4, output becomes step 5**

Renumber: old step 3 (GitHub comment) → step 4. Old step 4 (output) → step 5.

- [ ] **Step 4: Update graceful degradation table**

Find:
```
| No `docs/agents/` | Skip GitHub comment; still write handoff doc |
| No `session.json` | Use phase fallback chain above; create `session.json` from inferred values |
| No GitHub remote | Skip issue update; note "run /setup-harness-skills" |
| No memory system | Write key decisions inline in handoff doc under "Key decisions" |
```

Replace:
```
| No `.harness/` directory | Note "run /setup-harness-skills first"; write `.claude/handoff.md` as emergency fallback only |
| No `.continue-here.md` path resolvable | Write to `.harness/phases/XX-current/.continue-here.md` using STATE.md `current_focus` value |
| No `docs/agents/` | Skip GitHub comment; still write .continue-here.md |
| No `session.json` or STATE.md | Use phase fallback chain; create STATE.md from inferred values |
| No GitHub remote | Skip issue update silently |
| No memory system | Write key decisions inline in `<decisions_made>` section of .continue-here.md |
```

- [ ] **Step 5: Update output message**

Find:
```
- "Handover complete. Handoff doc: `.claude/handoff.md`."
- "**Start your next session with `/session-start`.**"
- "**To compact this session now, type `/compact`.**"
```

Replace:
```
- "Handover complete. Resume file: `.harness/phases/XX-name/.continue-here.md`."
- "**Start your next session with `/session-start`.**"
- "**To compact this session now, type `/compact`.**"
```

- [ ] **Step 6: Commit**

```bash
git add skills/engineering/context-handover/SKILL.md
git commit -m "feat(context-handover): write .continue-here.md in GSD format, set session_status idle"
```

---

### Task 7: Update context-handover Evals

**Files:**
- Modify: `evals/promptfoo/context-handover.yaml`

All three existing evals need fixture and assertion updates.

- [ ] **Step 1: Update eval #1 scaffold + assertions**

Find `scaffold_files` in eval #1:
```yaml
scaffold_files:
  - ".claude/session.json with execution phase and github issue 42"
  - "CLAUDE.md"
```

Replace:
```yaml
scaffold_files:
  - ".harness/STATE.md with idle session_status current_focus 03-execute and issue 42"
  - "CLAUDE.md"
```

Update assertions — replace:
```yaml
- type: llm-rubric
  value: Writes handoff doc to .claude/handoff.md — not a timestamped path or OS temp dir
```
With:
```yaml
- type: llm-rubric
  value: Writes .continue-here.md under .harness/phases/03-execute/ — not .claude/handoff.md or a timestamped path
- type: llm-rubric
  value: .continue-here.md includes YAML frontmatter with phase, task, status, last_updated fields
- type: llm-rubric
  value: .continue-here.md includes XML sections including <next_action> and <completed_work>
- type: llm-rubric
  value: Updates STATE.md Session Continuity to session_status idle
```

- [ ] **Step 2: Update eval #2 scaffold + assertions**

Replace `scaffold_files`:
```yaml
scaffold_files:
  - "package.json"
```
(unchanged — no STATE.md tests the fallback)

Update assertion:
```yaml
- type: llm-rubric
  value: Still writes a .continue-here.md or fallback handoff doc despite missing STATE.md
```

- [ ] **Step 3: Update eval #3 scaffold + assertions**

Replace `scaffold_files`:
```yaml
scaffold_files:
  - "CLAUDE.md"
  - "MEMORY.md"
  - ".harness/STATE.md with idle session_status current_focus 03-execute"
```

Update assertion:
```yaml
- type: llm-rubric
  value: .continue-here.md does not inline the content of MEMORY.md or any source files
- type: llm-rubric
  value: .continue-here.md references MEMORY.md by path only
- type: llm-rubric
  value: <next_action> reflects the user's stated focus on writing tests
```

- [ ] **Step 4: Run evals**

```bash
cd evals/promptfoo && promptfoo eval --config context-handover.yaml --no-cache
```

Expected: all 3 pass.

- [ ] **Step 5: Commit**

```bash
git add evals/promptfoo/context-handover.yaml
git commit -m "test(evals): update context-handover fixtures to .harness/ paths and GSD format"
```

---

## Chunk 4: State Machine — session-start

### Task 8: Update session-start SKILL.md

**Files:**
- Modify: `skills/engineering/session-start/SKILL.md`

This is the largest change — adds the state machine write step and the interrupted-recovery briefing branch.

- [ ] **Step 1: Replace the EXPLORE step (Step 1)**

Find:
```
- [ ] **1. EXPLORE** — read project state before asking anything:
  - `.claude/harness.json` → GitHub owner, repo, project board ID
  - `.claude/session.json` → phase, active task, effort estimate
  - `.claude/handoff.md` → last handover content
  - `.git/config` → remote origin (fallback if harness.json absent)
  - `CLAUDE.md` / `AGENTS.md` → `## Agent skills` block present? (setup indicator)
  - `docs/superpowers/specs/` → any `.md` files? (phase skip signal)
  - `MEMORY.md` or top-3 memory entries relevant to active task
```

Replace:
```
- [ ] **1. EXPLORE** — read project state before asking anything:
  - `.harness/STATE.md` → session_status, session_started, Current Position (phase, active task, status)
  - `.harness/STATE.md` → Session Continuity.Resume file → path to .continue-here.md
  - `.harness/config.json` → GitHub owner, repo, project board ID (harness key)
  - `.harness/phases/XX-name/.continue-here.md` → path from STATE.md Resume file
  - `.git/config` → remote origin (fallback if config.json absent)
  - `CLAUDE.md` / `AGENTS.md` → `## Agent skills` block present? (setup indicator)
  - `.harness/phases/01-discuss/` → any `CONTEXT.md` files? (phase skip signal)
  - `.harness/phases/02-plan/` → any `PLAN.md` files? (phase skip signal)
  - `MEMORY.md` or top-3 memory entries relevant to active task
  - `.claude/session.json` → legacy fallback if STATE.md absent (deprecated)
  - `.claude/handoff.md` → legacy fallback if .continue-here.md absent (deprecated)
```

- [ ] **Step 2: Add new Step 2 — WRITE SESSION STATE**

After Step 1 (EXPLORE), insert:

```
- [ ] **2. WRITE SESSION STATE** — update STATE.md Session Continuity before reading prior state:
  - Set `session_status: in_progress`
  - Set `session_started: <current ISO timestamp>`
  - Set `Active task: #N — [title]` in Current Position (if known from prior state or user context)
  - Budget: <1% of remaining context

  This makes the state machine transition observable: context-handover sets `session_status: idle`; session-start sets `session_status: in_progress`. A session that is interrupted before context-handover fires leaves `in_progress` in place — detected by the next session-start reading a stale `session_started` timestamp.
```

- [ ] **Step 3: Renumber and update RESUME CONTEXT (now Step 3)**

Replace the four-tier chain with the new chain:

```
- [ ] **3. RESUME CONTEXT** — determine if this is a clean resume or interrupted recovery:

  **Detect interrupted session:** if STATE.md `session_status` is `in_progress` AND `session_started` timestamp is >30 minutes old → this is an interrupted session. Output a **Recovery briefing** (see Step 6b).

  **Clean resume chain (session_status: idle or absent):**
  - **a. `.harness/phases/XX/.continue-here.md`** — primary. Read `<next_action>`, `<completed_work>`, `<remaining_work>`.
  - **b. Memory system query** — query active memory system for entries relevant to the active task. No GitHub required.
  - **c. Mid-session recovery** (.continue-here.md stale or absent): `git log --oneline -20` + recent GitHub per-AC progress comments (`gh api repos/{owner}/{repo}/issues/{N}/comments --jq '[.[] | select(.body | startswith("Progress"))] | .[-5:]'`).
  - **d. Legacy `.claude/handoff.md`** — use only if .continue-here.md absent and no migration has run.
  - **e. Cold start** — nothing found.
```

- [ ] **Step 4: Update EVALUATE step (now Step 4)**

Update the phase skip/revert table to use .harness/ artifact signals:

```
- [ ] **4. EVALUATE** — apply phase skip/revert (observable checks only):

  | Condition | Action |
  |---|---|
  | `.harness/phases/01-discuss/` contains a `CONTEXT.md` | Skip discuss → set phase to plan |
  | `.harness/phases/02-plan/` contains a `PLAN.md` | Skip discuss + plan → set phase to execute |
  | STATE.md `current_focus` is `02-plan` but no CONTEXT.md in `01-discuss/` | Revert to discuss |
  | STATE.md `current_focus` is `03-execute` but no PLAN.md in `02-plan/` | Revert to plan |

  Log skip/revert in the briefing: *"Phase advanced to execute — found PLAN.md in 02-plan and approved CONTEXT.md."*
```

- [ ] **Step 5: Update OUTPUT step (now Step 6) — two briefing formats**

Replace the single output format with two:

```
- [ ] **6. OUTPUT** — emit one of two briefing formats:

  **6a. Clean resume briefing:**
  ```
  ## Session briefing
  Phase: [discuss / plan / execute / verify] (0N-name)
  Active task: #N — [title]
  Effort remaining: ~N context window(s)
  Pick up from: [<next_action> from .continue-here.md]

  Budget for this session:
  [phase-specific table from context-handover/phase-budgets.md]

  Run /context-handover when approaching 80% usage.
  ```

  **6b. Recovery briefing (interrupted session detected):**
  ```
  ## Recovery briefing — interrupted session detected

  Previous session started: [session_started timestamp] — no context-handover was recorded.

  Phase: [from STATE.md Current Position]
  Active task: #N — [title]
  Last known intent: [Stopped at from STATE.md, or <next_action> from stale .continue-here.md]

  ## What changed since interruption (git log)
  [output of: git log --after="<session_started>" --oneline]

  ## What to do
  Review the git log above. If work is partially complete, continue from the last commit.
  If the session left code in an inconsistent state, run lint+build before proceeding.

  Run /context-handover when approaching 80% usage.
  ```
```

- [ ] **Step 6: Commit**

```bash
git add skills/engineering/session-start/SKILL.md
git commit -m "feat(session-start): add state machine write step and interrupted-recovery briefing"
```

---

### Task 9: Update session-start Evals

**Files:**
- Modify: `evals/promptfoo/session-start.yaml`

Three fixture updates + one new integration eval for interrupted recovery.

- [ ] **Step 1: Update eval #1 — full session state**

Replace `scaffold_files`:
```yaml
scaffold_files:
  - ".harness/STATE.md with idle session_status current_focus 03-execute and issue 7 effort 1"
  - ".harness/phases/03-execute/.continue-here.md with task 1 total_tasks 3"
  - "CLAUDE.md"
```

Update assertions to match new paths:
```yaml
assert:
  - type: llm-rubric
    value: Outputs a structured session briefing before doing anything else
  - type: llm-rubric
    value: Briefing includes phase (execute / 03-execute), active task number, and pick-up point from .continue-here.md
  - type: llm-rubric
    value: Includes the execute-phase budget table or references phase-budgets.md
  - type: llm-rubric
    value: Mentions running /context-handover when approaching 80% usage
  - type: llm-rubric
    value: Writes session_status in_progress to STATE.md before outputting briefing
  - type: llm-rubric
    value: Does not start writing code or taking actions before outputting the briefing
```

- [ ] **Step 2: Update eval #2 — no session state (unchanged scaffold, updated assertions)**

Scaffold is already minimal (`package.json`). Update one assertion wording to match new cold-start message:
```yaml
- type: llm-rubric
  value: Suggests running /setup-harness-skills to initialize .harness/ or asks user what to work on
```

- [ ] **Step 3: Update eval #3 — reads artifacts before asking questions**

Update scaffold:
```yaml
scaffold_files:
  - "package.json"
  - "CLAUDE.md"
  - ".harness/STATE.md with idle session_status current_focus 02-plan"
```

Update assertion:
```yaml
- type: llm-rubric
  value: Does not ask questions that could be answered by reading .harness/STATE.md or git config
```

- [ ] **Step 4: Add eval #4 — interrupted session recovery (NEW integration eval)**

```yaml
  # ---------------------------------------------------------------------------
  # Eval 4: Interrupted session — recovery briefing with git log diff
  # (Integration eval: tests session-start reading context-handover's state machine output)
  # ---------------------------------------------------------------------------
  - description: "#4 interrupted session — recovery briefing includes git log delta"
    vars:
      prompt: "/session-start"
      scaffold_files:
        - ".harness/STATE.md with interrupted session_status and stale timestamp and issue 42"
        - ".harness/phases/03-execute/.continue-here.md with task 2 total_tasks 5"
        - "CLAUDE.md"
    assert:
      - type: llm-rubric
        value: Detects interrupted session — STATE.md has session_status in_progress with stale timestamp
      - type: llm-rubric
        value: Outputs a Recovery briefing (not a normal Session briefing)
      - type: llm-rubric
        value: Recovery briefing includes a git log section showing changes since session_started timestamp
      - type: llm-rubric
        value: Recovery briefing includes the last known intent from STATE.md Stopped-at or .continue-here.md next_action
      - type: llm-rubric
        value: Advises reviewing git log before proceeding and running lint+build if state is inconsistent
      - type: llm-rubric
        value: Still writes session_status in_progress with new session_started timestamp to STATE.md
```

- [ ] **Step 5: Run evals**

```bash
cd evals/promptfoo && promptfoo eval --config session-start.yaml --no-cache
```

Expected: all 4 pass. If eval #4 fails, re-check the interrupted STATE.md scaffold pattern in scaffold_helper.py.

- [ ] **Step 6: Commit**

```bash
git add evals/promptfoo/session-start.yaml
git commit -m "test(evals): update session-start fixtures to .harness/ paths, add interrupted-recovery integration eval"
```

---

## Chunk 5: Content Skills + Gap Analysis

### Task 10: Update to-prd SKILL.md

**Files:**
- Modify: `skills/engineering/to-prd/SKILL.md`

- [ ] **Step 1: Update output destination**

Find the instruction about publishing and writing output. Add before "Write the PRD using the template below":

```
## GSD-compatible output

Write the PRD to `.harness/phases/01-discuss/01-CONTEXT.md` using GSD's 6-section CONTEXT.md format:

| GSD section | Content |
|---|---|
| `<domain>` | Phase boundary — what the discuss phase delivers (from user's stated scope) |
| `<decisions>` | Implementation decisions — WHAT the system must respect (maps to Technical Constraints) |
| `<canonical_refs>` | ADRs, spec sections, external docs cited during discussion |
| `<code_context>` | Brownfield: existing patterns, reusable assets, integration points |
| `<specifics>` | Specific user requirements ("I want it like X") |
| `<deferred>` | Ideas that came up but belong in other phases |

After writing: "CONTEXT.md written to `.harness/phases/01-discuss/01-CONTEXT.md`. Run `/to-issues` to plan this phase."

**WHAT/HOW invariant:** `<decisions>` contains only WHAT (constraints), never HOW (file paths, class names, schemas).
```

- [ ] **Step 2: Update the process description**

After step 3 "Write the PRD using the template below", add note: "For discuss-phase output, use the GSD CONTEXT.md format above instead of the prd-template."

- [ ] **Step 3: Run to-prd evals**

```bash
cd evals/promptfoo && promptfoo eval --config to-prd.yaml --no-cache
```

Update any failing eval assertions that check for `docs/superpowers/specs/` output path — replace with `.harness/phases/01-discuss/` assertions.

- [ ] **Step 4: Commit**

```bash
git add skills/engineering/to-prd/SKILL.md evals/promptfoo/to-prd.yaml
git commit -m "feat(to-prd): write GSD-compatible CONTEXT.md to .harness/phases/01-discuss/"
```

---

### Task 11: Update to-issues SKILL.md

**Files:**
- Modify: `skills/engineering/to-issues/SKILL.md`

- [ ] **Step 1: Add PLAN.md dual output step**

After step 5 "Publish the issues to the issue tracker", add:

```
### 6. Write .harness/phases/02-plan/02-PLAN.md (dual output)

In addition to GitHub Issues, write a GSD PLAN.md file. One task block per issue:

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

Path: `.harness/phases/02-plan/02-PLAN.md`. Create `.harness/phases/02-plan/` if absent.
```

- [ ] **Step 2: Update mid-session execution rules**

Add to the "Mid-session execution rules" section:
```
3. **PLAN.md is a local mirror** — GitHub Issues are the canonical human-visible record. PLAN.md is the GSD-compatible local record. Both are written simultaneously. If GitHub is not configured, write PLAN.md only.
```

- [ ] **Step 3: Run to-issues evals**

```bash
cd evals/promptfoo && promptfoo eval --config to-issues.yaml --no-cache
```

Update failing assertions to check for `.harness/phases/02-plan/02-PLAN.md` output.

- [ ] **Step 4: Commit**

```bash
git add skills/engineering/to-issues/SKILL.md evals/promptfoo/to-issues.yaml
git commit -m "feat(to-issues): add dual output PLAN.md to .harness/phases/02-plan/"
```

---

### Task 12: Update harness-engineering SKILL.md

**Files:**
- Modify: `skills/engineering/harness-engineering/SKILL.md`

Two changes: memory system detection at rank 4, extended step for .harness/ detection.

- [ ] **Step 1: Insert memory system step at rank 4**

The current order is: 1 Stop hook → 2 PostToolUse hook → 3 Instruction file → 4 CI → 5 Pre-commit → 6 Health script → 7 Onboarding config.

Renumber 4→5, 5→6, 6→7, 7→8. Insert new step 4:

```
### 4. Memory system
Check for any of these signals (one positive signal = gap closed):
- `.memobank/` directory present at root or user-level
- `mem0.json`, `letta.json`, or equivalent system config file at root
- `mem0`, `letta`, `memobank` in `requirements.txt`, `package.json`, or `pyproject.toml`
- Any mention of "mem0", "letta", "memobank", "memory system", "persistent memory" in CLAUDE.md / AGENTS.md
- `MEMORY.md` present (convention used by memobank and compatible systems)

No signal → **Gap: No memory system configured.** Why: mid-session interruption recovery falls back to GitHub per-AC comments (requires GitHub) or cold git-log reconstruction — no local recovery path exists without a memory system.
```

- [ ] **Step 2: Add .harness/ detection to step 8 (formerly 7) Onboarding config**

Extend step 8 (onboarding config) with:

```
Also check `.harness/config.json`:
- Absent → note "no GSD-compatible planning structure" (optional gap, not in top-5 priority)
- Present without `harness` key → "GSD detected but harness skills not configured" → after gaps, add: "GSD detected. Run `/setup-harness-skills` to configure GitHub integration."
- Present with `harness` key → **Already in place**: "GSD-compatible planning structure (.harness/)"
```

- [ ] **Step 3: Run harness-engineering evals**

```bash
cd evals/promptfoo && promptfoo eval --config harness-engineering.yaml --no-cache
```

Expect all existing evals to pass.

- [ ] **Step 4: Add new evals (in harness-engineering.yaml)**

Add two scenarios to `evals/promptfoo/harness-engineering.yaml`:

```yaml
  # ---------------------------------------------------------------------------
  # Eval N+1: .harness/config.json with harness key present — Already in place
  # ---------------------------------------------------------------------------
  - description: "#N+1 planning config with harness key — GSD-compatible setup in Already in Place"
    vars:
      prompt: "Please run harness-engineering on this project."
      scaffold_files:
        - ".claude/settings.json with stop and posttooluse hooks"
        - "CLAUDE.md"
        - ".harness/config.json with harness key"
    assert:
      - type: llm-rubric
        value: Lists GSD-compatible planning structure in the Already in place section
      - type: llm-rubric
        value: Does not list .harness/ as a gap when config.json with harness key is present

  # ---------------------------------------------------------------------------
  # Eval N+2: No memory system configured — memory system gap at rank 4
  # ---------------------------------------------------------------------------
  - description: "#N+2 no memory system — gap listed at rank 4"
    vars:
      prompt: "Please run harness-engineering on this project."
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - ".github/workflows/ci.yml with lint and build"
    assert:
      - type: llm-rubric
        value: Lists a memory system gap in the gap list
      - type: llm-rubric
        value: Gap message mentions at least two of mem0, letta, memobank, or equivalent
      - type: llm-rubric
        value: Memory system gap appears after stop hook and instruction file gaps (rank 4 or lower)
```

- [ ] **Step 5: Run all harness-engineering evals including new ones**

```bash
cd evals/promptfoo && promptfoo eval --config harness-engineering.yaml --no-cache
```

Expected: all evals including 2 new ones pass.

- [ ] **Step 6: Commit**

```bash
git add skills/engineering/harness-engineering/SKILL.md evals/promptfoo/harness-engineering.yaml
git commit -m "feat(harness-engineering): add memory system detection rank 4, extend .harness/ gap check"
```

---

### Task 13: Add setup-harness-skills New Eval Scenario

**Files:**
- Modify: `evals/promptfoo/setup-harness-skills.yaml`

- [ ] **Step 1: Add GSD-already-installed scenario**

```yaml
  # ---------------------------------------------------------------------------
  # Eval N+1: GSD already installed — should configure harness namespace, not overwrite
  # ---------------------------------------------------------------------------
  - description: "#N+1 GSD already installed — configure harness namespace without overwriting GSD keys"
    vars:
      prompt: "/setup-harness-skills"
      scaffold_files:
        - ".harness/config.json without harness key"
        - "CLAUDE.md"
        - ".git/config with remote origin"
    assert:
      - type: llm-rubric
        value: Detects .harness/config.json is present (GSD installed)
      - type: llm-rubric
        value: Adds harness namespace to config.json without overwriting existing GSD keys
      - type: llm-rubric
        value: Does NOT create a new config.json from scratch — merges into existing
      - type: llm-rubric
        value: Notes that GSD is already installed and confirms the integration
```

- [ ] **Step 2: Add missing `.harness/config.json` scaffold handler to scaffold_helper.py**

The handler for "without harness key" variant:
In scaffold_helper.py, the existing `.harness/config.json` handler already sets `has_harness = "harness key" in desc or "with harness" in desc`. The "without harness key" case already falls through to `config = {"model_profile": "balanced", "commit_docs": True}` — no extra code needed.

- [ ] **Step 3: Run setup-harness-skills evals**

```bash
cd evals/promptfoo && promptfoo eval --config setup-harness-skills.yaml --no-cache
```

- [ ] **Step 4: Commit**

```bash
git add evals/promptfoo/setup-harness-skills.yaml
git commit -m "test(evals): add setup-harness-skills GSD-already-installed scenario"
```

---

## Chunk 6: Full Eval Suite Run + Final Verification

### Task 14: Full Regression Run

- [ ] **Step 1: Run the complete eval suite**

```bash
python evals/run_evals.py
```

Expected: all skills pass. Note any regressions.

- [ ] **Step 2: Fix any regressions**

If a skill fails: `python evals/run_evals.py --skill <name>` to isolate. Fix the SKILL.md or scaffold, re-run until green.

- [ ] **Step 3: Verify CONTEXT.md has no remaining old vocabulary**

```bash
grep -n "\bDesign phase\b\|\bProduct phase\b\|\bExecution phase\b\|\bTesting phase\b" CONTEXT.md
grep -n "session\.json\|handoff\.md\|harness\.json" CONTEXT.md | grep -v "Deprecated\|deprecated\|legacy\|migration"
```

Expected: 0 matches for old phase names. Deprecated artifact terms only appear with deprecation notices.

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "chore: full GSD lifecycle adoption — all skills and evals updated"
```

---

## Out of Scope (do not implement)

- GSD's parallel wave execution (worktrees)
- GSD's 15-runtime installer
- GSD's knowledge graph (graphify)
- Automated GSD installation
- Deleting old `.claude/` artifact files (migration is offer-only, user confirms)
