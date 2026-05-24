# Harness Engineering Skill Collection — Design Spec

**Date:** 2026-05-24
**Status:** Approved — v3 (post-grill)
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
| **WHAT / HOW separation** | Product phase writes behavioral user stories (WHAT). Execution phase agent produces its own technical plan (HOW). User stories never contain file paths, implementation details, or code. |
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
│   │   ├── session-start/               ← NEW (phase detection + phase-skip/revert + briefing)
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

**Licensing note:** `mattpocock/skills` does not ship a LICENSE file as of the May 2026 snapshot used for this adaptation. All copied skills include an attribution comment at the top of SKILL.md: `# Adapted from https://github.com/mattpocock/skills`. Verify licensing before any public redistribution.

| Skill | Type | Change | Exact text changed |
|---|---|---|---|
| `zoom-out` | Engineering | None — copied verbatim | — |
| `caveman` | Productivity | None — copied verbatim | — |
| `grill-me` | Productivity | None — copied verbatim | — |
| `handoff` | Productivity | None — copied verbatim | — |
| `triage` | Engineering | One-line replacement | Replace: `run \`/setup-matt-pocock-skills\` if not` → `run \`/setup-harness-skills\` if not` |
| `to-prd` | Engineering | One-line replacement | Replace: `run \`/setup-matt-pocock-skills\` if not` → `run \`/setup-harness-skills\` if not` |
| `to-issues` | Engineering | One-line + BA format additions | (1) Replace: `run \`/setup-matt-pocock-skills\` if not` → `run \`/setup-harness-skills\` if not`. (2) Append BA user story format instructions (see below). |
| `write-a-skill` | Productivity | Add one checklist item | Append to the existing checklist section: `- [ ] Does the skill's description mention its typical context window cost?` |

#### `to-issues` — BA user story format additions

The adapted `to-issues` SKILL.md appends the following instructions after the existing mattpocock content:

```
## User story format (appended for this collection)

Each issue produced by /to-issues must follow BA best practices:

**Title:** [type]: short imperative description (e.g. "feature: user can reset password via email")

**Body structure:**
As a [role], I want [capability], so that [benefit].

### Acceptance Criteria
- [ ] Happy path: Given [context], when [action], then [outcome]
- [ ] Sad path: Given [context], when [error condition], then [expected error behaviour]
(add more AC rows as needed — minimum 1 happy + 1 sad)

### Definition of Ready
- [ ] Role, capability, and benefit are unambiguous
- [ ] All AC are written and testable
- [ ] Dependencies on other issues noted (link them)
- [ ] Effort estimate set in `Effort (windows)` field

### Definition of Done
- [ ] All AC pass
- [ ] PR merged to main
- [ ] No regressions in related tests
- [ ] Implementation notes written if agent deviated from spec

### Effort estimate
_Set by the Product phase agent. Unit = context windows (1 = fits in one session)._

---
**What vs. How:** This story describes WHAT the system should do. HOW to implement it
is determined by the Execution agent when it reads this issue. Do not add technical
implementation details, file paths, or code snippets to this story.
```

**INVEST criteria enforced at creation time:** `to-issues` checks each story before writing the issue. Two gates apply:
- A story that cannot be estimated (Estimable) must be refined before the issue is created.
- A story estimated at **>8 context windows must be split** into smaller issues before creation. 8 windows is the upper limit for a single issue; above this, the scope is too large to track and hand over reliably.

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

**`disable-model-invocation: true`** — a Claude Code skill metadata field that prevents this skill from being automatically triggered by Claude's skill selection logic. The skill only fires when the user explicitly types `/setup-harness-skills`. This is the correct behavior for a one-time gateway — accidental auto-triggering would overwrite user-edited config files. (Confirmed present in `mattpocock/skills` for `setup-matt-pocock-skills` and `zoom-out`.)

**Interaction style:** `setup-harness-skills` is a **dedicated setup session**, not a task skill. The 3-question limit in `harness-engineering` Phase 2 applies to diagnostic skills that must complete quickly during a working session. `setup-harness-skills` is intentionally invoked on its own — analogous to `npm init` or `gh repo create`. The five sections are: one question each, with a confirm-before-write gate at the end. Total interaction is 6–8 exchanges, which is appropriate for a one-time setup command.

**Interaction flow (one section at a time, never dump all at once):**

**Section A — Issue tracker**
> Explainer: Where do issues live? Skills like `triage`, `to-prd`, `to-issues` read from and write to it.
- GitHub Issues (uses `gh` CLI)
- GitHub Projects v2 (uses GraphQL API)
- Local markdown (`.scratch/<feature>/`)
- Other (user describes in prose)

**Section A.5 — Instruction file (runs only when neither CLAUDE.md nor AGENTS.md exists)**
> "No instruction file found. Which would you like to create?"
- `CLAUDE.md` — standard for Claude Code projects
- `AGENTS.md` — use when the project targets multiple AI agents (Codex, Kiro, Gemini, etc.)
Do NOT make this choice unilaterally. Wait for the user's answer before proceeding.

**Section B — Triage label vocabulary**
> Explainer: Five canonical roles: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. Override if your repo uses different strings.

**Section C — Domain docs**
> Explainer: Single-context (one CONTEXT.md + docs/adr/) or multi-context (CONTEXT-MAP.md for monorepos)?

**Section D — GitHub Project board + Milestones** *(new, not in mattpocock/skills)*
> Explainer: The `context-handover` and `session-start` skills track long-running tasks on a GitHub Project board. Which board? What are your column names for Backlog / In Progress / Done? Also: what Milestones should be created? (Defaults: `Design`, `MVP`, `v1.0` — override or skip.)

**Section E — Session state location** *(new)*
> Explainer: `.claude/session.json` tracks the active phase and task across sessions. Confirm this location or override it.

**Output after all five sections:**

1. Confirm draft of `## Agent skills` block with user before writing
   - If an `## Agent skills` section already exists in CLAUDE.md / AGENTS.md: show diff (old block → new block), not just the new block
   - If not found: show new block and confirm append
2. Write block to whichever of CLAUDE.md / AGENTS.md exists (never create the other)
   - **Idempotent write:** if `## Agent skills` already exists, replace the existing block in-place; never append a second copy
3. Write `.claude/harness.json` with GitHub owner, repo, project board ID, branch, and paths confirmed in Sections A–E (idempotent — merge over existing values if file already exists)
4. Create GitHub labels via `gh label create` (all four categories — idempotent)
5. Create GitHub Milestones via `gh api` (user-confirmed names from Section D)
6. Create GitHub Project v2 board if user opted in (Section D), with `Effort (windows)` field; write `project_v2_id` back to `harness.json`
7. Configure branch protection via `gh api` (graceful degradation on permission failure)
8. Scaffold `.github/workflows/ci.yml` (stack-specific)
9. Append to `.gitignore` (idempotent — skip lines already present):
   ```
   .claude/handoff.md      # agent session handoff — never commit
   .claude/session.json    # agent session state — never commit
   ```
   `.claude/harness.json` is NOT gitignored — it is committed as shared team config
   (analogous to `package.json`). The whole team shares the same GitHub owner, repo,
   project board ID, and branch via this file.

10. Write seed files to `docs/agents/`:
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
  instruct the user to compact the context window so a fresh session can resume
  seamlessly. Invoke manually with /context-handover [next-session-focus] when
  approaching 80% context window usage (Claude reports this natively).
argument-hint: "What will the next session focus on?"
```

**Phase detection (in priority order):**
1. Read `.claude/session.json` → `current_phase` field. Use this if the file exists AND `current_phase` is non-null.
2. **Fallback** (session.json absent OR `current_phase` is null/missing): read active GitHub issue labels → `phase:design / phase:product / phase:execution / phase:testing` maps directly.
3. **Fallback** (no phase label): read issue title and body, infer from task keywords ("write PRD", "design" → product; "implement", "build", "fix" → execution; "test", "QA", "verify" → testing; "design", "spec", "ADR" → design).
4. **Fallback** (still unknown): default to `execution`, note "phase inferred by default" in handoff doc.

The session.json is the authoritative source because it is written by this collection's own skills and reflects the user's declared intent. GitHub issue labels are a human-readable secondary source that the onboarding skill (`setup-harness-skills`) documents in `docs/agents/`. The two are not in conflict — session.json is writable by agents, labels by humans — but session.json takes precedence when present.

**Execution sequence:**

```
1. Save memory
   → Invoke memobank skill if installed
   → Write key decisions to MEMORY.md if memobank absent
   Budget: <5% of remaining context

2. Update unified handoff doc
   → Path: `.claude/handoff.md` (project-local; added to .gitignore by setup-harness-skills)
   → This is a **single, unified file** — overwritten in place on every handover. No timestamps in the path.
   → Content per phase (see phase-budgets.md):
      Design: decisions made, open questions, next doc to write
      Product: stories broken down, next story, effort remaining
      Execution: code written, test status, next file/function
      Testing: issues found, root causes, next test case
   → Reference artifacts by path/URL only — never inline content
   → Include "Suggested skills" section
   → Always include "Last updated: [YYYY-MM-DD HH:mm]" at the top
   Budget: <5% of remaining context

3. Update GitHub issue (if docs/agents/issue-tracker.md exists AND active task has a GitHub issue)
   → Append handoff content as issue comment (see format below)
   → Update session.json: last_handover, next_session_hint
   → GitHub issue comment is the **durable remote record** for humans;
     `.claude/handoff.md` is the **primary local record** for the next agent session.

   **Issue comment format (multi-session progress log):**
   ```
   ## Handover — [YYYY-MM-DD HH:mm]

   **Phase:** [execution]
   **Session summary:** [1–3 sentences on what was done this session]
   **Next step:** [specific pick-up point for the next session]
   **Handoff doc:** `.claude/handoff.md`

   _[N] of ~[effort_estimate] context window(s) used so far._
   ```
   Comments accumulate on the issue across sessions, forming a
   visible progress log for humans.
   The issue is only closed when all AC pass and PR is merged — not at handover.

4. Output to user
   → "Handover complete. Handoff doc: `.claude/handoff.md`."
   → Print: "**Start your next session with `/session-start`.**"
   → Print: "**To compact this session now, type `/compact`.**"
   → Do NOT programmatically invoke `/compact` — it is a user-invoked built-in slash command. The skill instructs the user to invoke it. The user is always in control of when context is cleared.
```

**Handoff doc path:** `.claude/handoff.md` — fixed, project-local, overwritten each handover.
- Eliminates cross-platform temp dir resolution.
- Added to `.gitignore` by `setup-harness-skills` so it is never committed.
- Accessible across restarts (unlike OS temp dirs that may be cleared).
- `session-start` reads this path directly — no glob needed.

**Graceful degradation of `context-handover`:**
- No `docs/agents/` config: skip GitHub issue update step; still write handoff doc and update session.json
- No session.json: use phase fallback chain (see Phase detection above); create session.json from inferred values
- No GitHub remote: skip issue update silently; note "no issue tracker configured — run /setup-harness-skills"
- No memobank installed and no MEMORY.md: write a brief memory note inline in the handoff doc under "Key decisions"

**Reference file:** `context-handover/phase-budgets.md` — defines what each phase's handoff focuses on AND the budget percentage tables (same tables used by `session-start`). Content schema:

```markdown
# Phase Budgets

## [Phase name]

### Session budget
| Activity | Budget |
|---|---|
| Reading prior context | <N% |
| ... | ... |

### Handoff focuses on
- [item 1]
- [item 2]
```

Four phases: Design, Product, Execution, Testing. Full table values defined in Section 5.3 of this spec.

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

**Phase skip / revert logic (runs before outputting briefing):**

`session-start` evaluates existing artifacts to determine the appropriate starting phase, overriding `session.json.current_phase` when the evidence warrants it:

All conditions are **artifact-observable only** — phase revert is never triggered by the agent's subjective quality judgment about artifact content. If an artifact exists but seems thin, proceed and note the concern in the issue comment.

| Condition (observable check) | Action |
|---|---|
| At least one `.md` file exists in `docs/superpowers/specs/` | Skip Design — set phase to Product |
| `phase:execution` issues exist with `status:ready-for-agent` (and spec exists) | Skip Design + Product — set phase to Execution |
| No `.md` file in `docs/superpowers/specs/` | Revert to Design — update `session.json.current_phase`, comment on Design Phase Tracking Issue |
| `current_phase == "product"` but no `phase:design` issue is closed or labelled `design-approved` | Revert to Design — design approval gate not passed |
| `current_phase == "execution"` but `gh issue list --label "phase:execution,status:ready-for-agent"` returns 0 issues | Revert to Product — no ready issues to execute |

Phase skip/revert is logged in the session briefing: *"Phase advanced to Execution — found 3 ready-for-agent issues and an approved spec."* or *"Phase reverted to Design — no spec found in docs/superpowers/specs/."*

**Execution sequence:**

```
1. Read .claude/harness.json → GitHub owner, repo, project board ID, default branch
   Read .claude/session.json (if exists) → phase, active task, effort estimate
2. Resume context — handoff doc is PRIMARY:
   a. Read `.claude/handoff.md` (fixed path — no glob needed)
   b. Fetch last GitHub issue comment ONLY when `.claude/handoff.md` is absent,
      AND any of the following is true:
        - local project context is completely lost (handoff file deleted or project re-cloned)
        - severe task deviation detected: active_task in session.json doesn't match the current
          GitHub `in-progress` issue (different issue number)
        - user explicitly requests a GitHub sync ("sync from GitHub", "what's on the issue", etc.)
      Command: gh api repos/{owner}/{repo}/issues/<N>/comments --jq '.[-1]'
      (fetches the single last comment only — never the full comment history)
   c. Full comment history: NEVER loaded automatically. Load only if user explicitly requests
      ("show me all handover history for this issue").
3. Read MEMORY.md or top-3 memobank entries relevant to active task
5. Evaluate artifact evidence → apply phase skip/revert if warranted (see above)
6. If session.json absent after evaluation: infer phase from GitHub issue state + labels
7. Output structured briefing:
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

### 5.4 Context window monitoring — no hook required

Claude Sonnet 4.6 / 4.5 and Haiku 4.5 receive native context awareness via `<system_warning>Token usage: X/Y; Z remaining</system_warning>` injected after each tool call. No PostToolUse hook is needed to detect 80% usage — Claude receives this signal directly and can invoke `/context-handover` based on it.

A PostToolUse hook that reads `$CLAUDE_CONTEXT_USAGE_PCT` was considered and rejected: the env var name is unverified in Claude Code's hook runtime, and the GitHub OAuth endpoint (`/api/usage`) returns subscription quota (5-hour/7-day billing windows), not context window usage — making external monitoring unreliable. Native awareness is more accurate and requires zero infrastructure.

**`setup-harness-skills` does not write any context-monitoring hook.** The `context-handover` SKILL.md instructs Claude to invoke `/context-handover` when it detects the native 80% warning.

---

### 5.5 `.claude/harness.json` — Static Project Config

Separates static project configuration (what this project is) from dynamic session state (what is happening right now). Written by `setup-harness-skills` once at project start; updated only when the user re-runs setup to change a setting.

```json
{
  "schema_version": 1,
  "github": {
    "owner": "my-org",
    "repo": "my-project",
    "default_branch": "main",
    "project_v2_id": "PVT_xxxx",
    "project_board_name": "My Project Board"
  },
  "docs_agents_dir": "docs/agents",
  "specs_dir": "docs/superpowers/specs",
  "issue_tracker": "github"
}
```

**All fields populated by `setup-harness-skills`.** Skills read this file with null-safety: if `github.project_v2_id` is null, skip Project board update steps silently.

Written by: `setup-harness-skills`.
Read by: `session-start`, `context-handover`, `harness-engineering`, `to-issues`.

---

### 5.6 `.claude/session.json` — Dynamic Session State

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
  "last_handover": "2026-05-24T10:30:00Z",
  "next_session_hint": "Continue from writing context-monitor.sh — bash conditional logic done, need to test with real token env var"
}
```

**Optional fields:**
- `active_task.github_issue` — null/absent if using local markdown tracker
- `active_task.github_project_item_id` — null/absent if no GitHub Projects v2 board configured or if using local/other tracker
Skills read these fields with null-safety: if `github_issue` is null, skip GitHub update steps silently.

Written by: `session-start` (initializes), `context-handover` (updates).
Read by: `session-start`, `context-handover`, `harness-engineering`.

---

### 5.7 GitHub Data Model

**Label schema** — four categories applied to all issues:

| Category | Values |
|---|---|
| `status:` | `triage` / `needs-prd` / `ready-for-agent` / `in-progress` / `done` |
| `phase:` | `design` / `product` / `execution` / `testing` |
| `type:` | `feature` / `bug` / `chore` / `task` |
| `priority:` | `p1` / `p2` / `p3` |

`phase:` is **categorical** — it describes what kind of issue this is, not what phase the project is currently in. A `phase:execution` issue and a `phase:testing` issue can coexist on the board. The canonical current project phase is `session.json.current_phase`; the agent processes only issues matching `phase:<current-phase>` + `status:ready-for-agent`.

**`setup-harness-skills` creates all labels** via `gh label create`. If a label already exists, the command is skipped (idempotent).

**Status flow (mirrors mattpocock/skills):**
```
triage → needs-prd → ready-for-agent → in-progress → done
```
Agent moves issues forward. Human can move backward (e.g., `ready-for-agent` → `needs-prd` to signal rework needed).

**GitHub Milestones** — native GitHub grouping containers, not issue types. Created by `setup-harness-skills` at project start. Suggested defaults: `Design`, `MVP`, `v1.0`. Issues are assigned to milestones during the Product phase breakdown. Milestones give humans a progress view per release on the GitHub Project board. Not represented as labels — use `gh milestone create` and `gh issue edit --milestone`.

**GitHub Project v2 board** — created by `setup-harness-skills` via GraphQL API if user opts in during Section D:
- Default columns: `Backlog` / `In Progress` / `Done`
- Custom field: `Effort (windows)` — number field, agent-estimated context windows to complete per issue
- Issues are added to the board at creation; column matches `status:` label

**Phase Exit Criteria oracles:**

| Phase | Oracle |
|---|---|
| Design | Design Phase Tracking Issue (`phase:design`) has label `design-approved` or is closed by human |
| Product | All `phase:execution` issues created from breakdown have `status:ready-for-agent` |
| Execution | All `phase:execution` issues are closed via merged PRs (`Closes #NNN` in PR body) |
| Testing | All `phase:testing` issues are `status:done`; no open `p1` bugs remain |

**Branch protection (Execution oracle prerequisite):**

PR merge is the Execution phase oracle. For it to be unforgeable, `setup-harness-skills` configures branch protection on `main` via `gh api`:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field enforce_admins=true \
  --field 'required_status_checks={"strict":true,"contexts":["ci"]}' \
  --field 'required_pull_request_reviews={"required_approving_review_count":0}' \
  --field restrictions=null
```

**Graceful degradation:** If this call fails (insufficient token permissions), the failure is recorded as an unresolved gap and printed in the setup summary under "Requires manual action." Other setup steps continue. The required permission is `admin:repo` (or repo admin role).

**GitHub Actions CI workflow** — `setup-harness-skills` scaffolds `.github/workflows/ci.yml` (stack-specific, based on stack detected during setup). This is a hard dependency for branch protection to have a status check to require.

---

## 6. Enhanced `harness-engineering` Skill

**Exact change to SKILL.md** — add as step 11 in Phase 1 detection:

```
11. Check onboarding config: `docs/agents/` directory — exists with harness skill config files?
    → If yes: mark as "setup-harness-skills has been run" in the Already in Place list.
    → If no: after the main gap list, append:
      "**Optional:** Run `/setup-harness-skills` to configure GitHub Project integration,
       session state tracking, and context handover — this extends the harness to cover
       long-running multi-session work."
```

**No other changes to SKILL.md.** The suggestion is appended after the prioritized gap list, so it never displaces Stop hook as gap #1. The existing evals (IDs 1–6) are not affected.

**Two new evals added to `harness-engineering/evals/evals.json`:**

```json
{
  "id": 7,
  "prompt": "Check the harness for my project. It has docs/agents/ with issue-tracker.md, triage-labels.md, domain.md, github-project.md, and session-config.md.",
  "scaffold": { "has_docs_agents": true, "all_five_agent_docs": true, "no_claude_settings": false },
  "expectations": [
    "Lists 'setup-harness-skills configured' in the Already in Place section",
    "Does NOT suggest running /setup-harness-skills (already done)"
  ]
},
{
  "id": 8,
  "prompt": "Set up harness for my project.",
  "scaffold": { "no_docs_agents": true, "no_claude_settings": true },
  "expectations": [
    "Stop hook is still gap #1",
    "After the main gap list, suggests running /setup-harness-skills as an optional step",
    "The suggestion does NOT appear before gap #1"
  ]
}
```

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

### Eval file architecture

Each skill directory that has evals ships its own `evals/evals.json`. This is consistent with the current `harness-engineering/evals/evals.json` pattern. No shared top-level evals file.

`run_evals.py` is enhanced to:
- Accept `--skill <name>` flag: loads `skills/*/<name>/evals/evals.json` and runs only those evals
- Default (no flag): discovers all `skills/*/*/evals/evals.json` files and runs them all, grouped by skill name in output
- The eval runner's existing `--evals N[,N]` flag applies within the selected skill's evals only

### Draft eval content (to be written to `evals/evals.json` per skill at implementation time)

**`setup-harness-skills` — 3 evals**

```json
[
  {
    "id": 1,
    "prompt": "I'm starting a new Next.js project and want to use harness skills. Please set up the harness.",
    "scaffold": { "files": ["package.json"], "github_remote": "owner/my-next-app", "has_claude_md": true, "has_agents_md": false },
    "expectations": [
      "Asks about issue tracker before writing any files",
      "Asks each of the five sections one at a time, not all at once",
      "Writes docs/agents/issue-tracker.md",
      "Writes docs/agents/triage-labels.md",
      "Writes docs/agents/domain.md",
      "Writes docs/agents/github-project.md",
      "Writes docs/agents/session-config.md",
      "Adds ## Agent skills block to CLAUDE.md (not AGENTS.md)",
      "Does NOT create AGENTS.md when CLAUDE.md exists"
    ]
  },
  {
    "id": 2,
    "prompt": "I want to update the harness setup. docs/agents/issue-tracker.md already exists.",
    "scaffold": { "has_docs_agents": true, "existing_issue_tracker_md": true, "has_claude_md": true },
    "expectations": [
      "Detects existing docs/agents/ config and notes it",
      "Updates in-place rather than overwriting with defaults",
      "Does not re-ask questions that are already answered in existing config"
    ]
  },
  {
    "id": 3,
    "prompt": "Set up harness skills for this project. There's no CLAUDE.md or AGENTS.md yet.",
    "scaffold": { "has_claude_md": false, "has_agents_md": false },
    "expectations": [
      "Asks the user which instruction file to create (CLAUDE.md or AGENTS.md)",
      "Does NOT make the choice unilaterally",
      "Creates only the file the user specifies"
    ]
  }
]
```

**`context-handover` — 3 evals**

```json
[
  {
    "id": 1,
    "prompt": "WARNING: Context at 82%. Run /context-handover before continuing.",
    "scaffold": { "session_json": { "current_phase": "execution", "active_task": { "github_issue": 42, "title": "Add auth middleware" } }, "has_github_remote": true },
    "expectations": [
      "Identifies current phase as 'execution' from session.json",
      "Writes handoff doc to .claude/handoff.md (not a timestamped temp file)",
      "Handoff doc references the GitHub issue by number/URL, not by inlining issue body",
      "Updates .claude/session.json with last_handover timestamp",
      "Instructs user to start a new session with /session-start"
    ]
  },
  {
    "id": 2,
    "prompt": "Please do a context handover. I'm getting close to the limit.",
    "scaffold": { "no_session_json": true, "github_issue_labels": ["phase:product"], "github_issue_title": "Write PRD for user auth" },
    "expectations": [
      "Detects no session.json and falls back to GitHub issue label",
      "Correctly identifies phase as 'product' from label",
      "Still writes a handoff doc successfully",
      "Does NOT error or refuse due to missing session.json"
    ]
  },
  {
    "id": 3,
    "prompt": "Context handover — next session will focus on writing tests.",
    "scaffold": { "session_json": { "current_phase": "execution" }, "has_memory_md": true },
    "expectations": [
      "Handoff doc does not inline the content of MEMORY.md or any code files",
      "Handoff doc references MEMORY.md by path only",
      "next_session_hint in session.json reflects the user's stated focus ('writing tests')"
    ]
  }
]
```

**`session-start` — 3 evals**

```json
[
  {
    "id": 1,
    "prompt": "/session-start",
    "scaffold": { "session_json": { "current_phase": "execution", "active_task": { "github_issue": 7, "title": "Implement login flow", "effort_estimate": 1 }, "next_session_hint": "Continue from UserService.login()" }, "handoff_doc": ".claude/handoff.md" },
    "expectations": [
      "Outputs a structured session briefing",
      "Briefing includes: phase, active task, effort estimate, next step from handoff doc",
      "Includes the execution-phase budget table",
      "Does not start writing code immediately without briefing the user first"
    ]
  },
  {
    "id": 2,
    "prompt": "/session-start",
    "scaffold": { "no_session_json": true, "no_handoff_doc": true },
    "expectations": [
      "Does not error or refuse",
      "Outputs a briefing noting no prior session state was found",
      "Asks user what they want to work on, or suggests running /setup-harness-skills"
    ]
  },
  {
    "id": 3,
    "prompt": "/session-start",
    "scaffold": { "no_session_json": true, "github_issue_labels": ["phase:product"], "github_issue_title": "Break down auth epic into stories" },
    "expectations": [
      "Infers phase as 'product' from GitHub issue label",
      "Outputs the product-phase budget table",
      "Does not output the execution-phase budget table"
    ]
  }
]
```

---

## 9. Implementation Order

| Phase | What | Why |
|---|---|---|
| 1 | Repo restructure | Clean foundation — move files, create `.claude-plugin/`, update `plugin.json` |
| 2 | `setup-harness-skills` | Gateway — needed by everything else |
| 3 | `context-handover` + `session-start` | Core new value |
| 4 | Adapt mattpocock skills | Low-effort: one-line change each |
| 5 | Enhance `harness-engineering` | Read `docs/agents/` config |
| 6 | Eval runner + new evals | Verify all skills pass |

Each phase is one implementation plan / spec cycle.

---

## 10. Out of Scope

- `prototype`, `tdd`, `improve-codebase-architecture`, `grill-with-docs`, `diagnose` (use mattpocock/skills)
- Multi-agent orchestration beyond subagent spawning
- Non-GitHub issue trackers in the initial version (noted in Section D as extensible)
- **Automated session chaining** — Desktop tasks, `/loop`, Routines. Session continuation is manual: user runs `/compact` or `/new`, then `/session-start` to resume. Automation is a future nice-to-have; the handoff document is the primary continuity mechanism.
- PostToolUse context-monitoring hooks — Claude's native context awareness (`<system_warning>Token usage: X/Y; Z remaining</system_warning>`) replaces this need entirely.
