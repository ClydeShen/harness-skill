# Setup-Harness-Skills — Implementation Plan (Plan 2)

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `setup-harness-skills` gateway skill: SKILL.md with full 5-section interaction flow, 6 bundled seed templates, 3 evals, and plugin.json registration.

**Architecture:** Pure markdown/JSON authoring — no runtime code. SKILL.md drives the interactive session; seed templates are written to docs/agents/ in the target project. Evals verify the explore-first pattern, idempotency, and CLAUDE.md/AGENTS.md choice gate.

**Tech Stack:** Markdown (SKILL.md, seed templates), JSON (evals.json, plugin.json).

---

## Chunk 1: SKILL.md

### Task 1: Create skill directory and SKILL.md

**Files:**
- Create dir: `skills/engineering/setup-harness-skills/`
- Create dir: `skills/engineering/setup-harness-skills/evals/`
- Create: `skills/engineering/setup-harness-skills/SKILL.md`

- [ ] **Step 1: Create directories**

```bash
mkdir -p skills/engineering/setup-harness-skills/evals
```

- [ ] **Step 2: Write SKILL.md**

Create `skills/engineering/setup-harness-skills/SKILL.md` with this exact content:

```markdown
---
name: setup-harness-skills
description: >
  Sets up an ## Agent skills block in AGENTS.md/CLAUDE.md and docs/agents/ so
  harness skills know the issue tracker, triage labels, domain docs, GitHub
  Project board, and session state location. Run before first use of triage,
  to-prd, to-issues, context-handover, or session-start — or if those skills
  appear to be missing context. Typically consumes <30% of a context window.
disable-model-invocation: true
---

# Adapted from https://github.com/mattpocock/skills (MIT License)

You are running `/setup-harness-skills`. This is a **one-time gateway** for a project — it configures the harness so all other skills know the issue tracker, label vocabulary, domain docs, and session state location.

**Interaction style:** Dedicated setup session. Always explore first, then ask questions one section at a time. Never dump all questions at once.

---

## Step 1 — Explore (before asking anything)

Read and report a **one-line summary** of what you found:

1. `.git/config` → remote origin (owner/repo)
2. `CLAUDE.md` / `AGENTS.md` → existing `## Agent skills` block?
3. `CONTEXT.md` → present?
4. `docs/agents/` → prior setup files?
5. `.claude/harness.json` → prior config?

Example: "Found CLAUDE.md with no Agent skills block, no docs/agents/, GitHub remote owner/repo."

Then proceed to Section A.

---

## Section A — Issue Tracker

> "Where do issues live? Skills like `triage`, `to-prd`, and `to-issues` read from and write to it."

Options (present as numbered list):
1. **GitHub Issues** — standard `gh issue` CLI commands
2. **GitHub Projects v2** — GraphQL API board with custom fields
3. **Local markdown** — files in `.scratch/<feature>/`
4. **Other** — describe in prose

Wait for answer before proceeding to Section B.

---

## Section A.5 — Instruction File

**Run this section ONLY if neither CLAUDE.md nor AGENTS.md exists.**

> "No instruction file found. Which would you like to create?"
> 1. `CLAUDE.md` — standard for Claude Code projects
> 2. `AGENTS.md` — use when targeting multiple AI agents (Codex, Kiro, Gemini, etc.)

Do NOT choose unilaterally. Wait for the user's answer before proceeding.

---

## Section B — Triage Label Vocabulary

> "Five canonical status labels are used by all harness skills: `status:needs-triage`, `status:needs-info`, `status:ready-for-agent`, `status:ready-for-human`, `status:wontfix`. The harness also adds: `status:needs-prd`, `status:needs-review`, `status:in-progress`, `status:done`. Are these the right strings for your repo, or do you use different ones?"

Accept the defaults (user just says "yes" or "looks good") or wait for overrides. Note any overrides before proceeding to Section C.

---

## Section C — Domain Docs

> "Is this a single-context repo (one CONTEXT.md + docs/adr/) or a multi-context repo (CONTEXT-MAP.md pointing to multiple bounded contexts)?"

Options:
1. **Single-context** — one CONTEXT.md at root
2. **Multi-context** — CONTEXT-MAP.md with multiple bounded contexts (monorepo)
3. **Neither yet** — I'll create CONTEXT.md later

Wait for answer before proceeding to Section D.

---

## Section D — GitHub Project Board + Milestones

> "The `context-handover` and `session-start` skills track long-running tasks on a GitHub Project board."
>
> "Which board should they use? (Leave blank to skip board integration.)"

If the user provides a board:
> "Default column names: `Triage`, `Needs PRD`, `Needs Review`, `Ready for Agent`, `In Progress`, `Done`. Are these right for your board, or use different names?"

Then:
> "What milestones should be created? Defaults: `Design`, `MVP`, `v1.0`. Override or type 'skip'."

Wait for answer before proceeding to Section E.

---

## Section E — Session State Location

> "`.claude/session.json` tracks the active phase and task across sessions. Is `.claude/session.json` the right location, or do you want to use a different path?"

Accept confirmation or override. Then proceed to output.

---

## Output (after all five sections confirmed)

Work through these steps in order.

**1. Show `## Agent skills` block draft — confirm before writing**

If `## Agent skills` already exists: show diff (old → new block).
If not found: show the new block and confirm append location.

**2. Write block** to whichever of CLAUDE.md / AGENTS.md exists (never create the other).
- Idempotent: replace existing block in-place — never append a second copy.

**3. Write `.claude/harness.json`** (merge over existing values if file already exists):

```json
{
  "schema_version": 1,
  "github": {
    "owner": "<from .git/config>",
    "repo": "<from .git/config>",
    "default_branch": "main",
    "project_v2_id": null,
    "project_board_name": null
  },
  "docs_agents_dir": "docs/agents",
  "specs_dir": "docs/superpowers/specs",
  "issue_tracker": "<from Section A>"
}
```

**4. Create GitHub labels** via `gh label create` (skip if label already exists — idempotent):

```bash
# Status labels
gh label create "status:triage" --color "#e4e669"
gh label create "status:needs-prd" --color "#d4c5f9"
gh label create "status:needs-review" --color "#f9c846"
gh label create "status:needs-info" --color "#f9c846"
gh label create "status:ready-for-agent" --color "#0075ca"
gh label create "status:in-progress" --color "#e99695"
gh label create "status:done" --color "#0e8a16"
gh label create "status:wontfix" --color "#ffffff"
gh label create "status:ready-for-human" --color "#cfd3d7"

# Phase labels
gh label create "phase:design" --color "#c2e0c6"
gh label create "phase:product" --color "#bfd4f2"
gh label create "phase:execution" --color "#fef2c0"
gh label create "phase:testing" --color "#f9d0c4"

# Type labels
gh label create "type:feature" --color "#84b6eb"
gh label create "type:bug" --color "#ee0701"
gh label create "type:chore" --color "#e4e669"
gh label create "type:task" --color "#bfd4f2"
gh label create "type:spike" --color "#d4c5f9"

# Priority labels
gh label create "priority:p1" --color "#b60205"
gh label create "priority:p2" --color "#e4e669"
gh label create "priority:p3" --color "#cfd3d7"
```

Note: `status:needs-review` is required — it is the Product exit human gate.

If `gh label create` fails because the label already exists, continue (idempotent).

**5. Create GitHub Milestones** (if user provided names in Section D):

```bash
gh api repos/{owner}/{repo}/milestones --method POST --field title="Design"
gh api repos/{owner}/{repo}/milestones --method POST --field title="MVP"
gh api repos/{owner}/{repo}/milestones --method POST --field title="v1.0"
```

Skip any milestone that already exists.

**6. Create GitHub Project v2 board** (only if user opted in during Section D):
- Create board via `gh project create`
- Add `Effort (windows)` number field
- Write `project_v2_id` and `project_board_name` back to `harness.json`

**7. Configure branch protection** on `main`:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field enforce_admins=true \
  --field 'required_status_checks={"strict":true,"contexts":["ci"]}' \
  --field 'required_pull_request_reviews={"required_approving_review_count":0}' \
  --field restrictions=null
```

If this fails (insufficient permissions): record as "Requires manual action" in the setup summary. Continue other steps.

**8. Scaffold `.github/workflows/ci.yml`** (stack-specific, based on files detected in Step 1):
- Node.js (package.json present): Node CI template
- Python (requirements.txt / pyproject.toml): Python CI template
- Unknown stack: minimal placeholder CI

**9. Append to `.gitignore`** (idempotent — skip lines already present):

```
.claude/handoff.md
.claude/session.json
```

Note: `.claude/harness.json` is NOT gitignored — it is committed as shared team config.

**10. Write seed files to `docs/agents/`** from bundled templates in this skill's folder:

```
docs/agents/issue-tracker.md    ← copy from issue-tracker-github.md or issue-tracker-github-projects.md
docs/agents/triage-labels.md    ← copy from triage-labels.md
docs/agents/domain.md           ← copy from domain.md
docs/agents/github-project.md   ← copy from github-project.md
docs/agents/session-config.md   ← copy from session-config.md
```

After all steps, print a **setup summary**:
- ✅ Items completed
- ⚠️ Items requiring manual action (e.g., branch protection, unknown stack)
- 📁 Files written to `docs/agents/`

Then: "Run `/session-start` to begin your first session."

---

_🤖 All comments and issue bodies posted by this skill end with this footer._
```

- [ ] **Step 3: Verify SKILL.md line count is ≤500**

```bash
wc -l skills/engineering/setup-harness-skills/SKILL.md
```
Expected: under 200 lines (well within 500-line limit).

- [ ] **Step 4: Commit**

```bash
git add skills/engineering/setup-harness-skills/
git commit -m "feat(setup-harness-skills): add SKILL.md with 5-section interaction flow"
```

---

## Chunk 2: Seed Templates

### Task 2: Create issue-tracker-github.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/issue-tracker-github.md`

- [ ] **Step 1: Write issue-tracker-github.md**

```markdown
# Issue Tracker: GitHub Issues

## Commands

```bash
# Create issue
gh issue create --title "type: description" --body "..." --label "status:triage,phase:execution"

# List ready issues for current phase
gh issue list --label "status:ready-for-agent,phase:execution"

# View issue
gh issue view <N>

# Update label (move forward)
gh issue edit <N> --add-label "status:in-progress" --remove-label "status:ready-for-agent"

# Close issue
gh issue close <N>

# Add comment
gh issue comment <N> --body "..."
```

## Conventions

- Title format: `[type]: short imperative description` (e.g., `feature: user can reset password via email`)
- All issues follow the enforced template: Story / Confidence / AC / DoD / Effort / Dependencies
- Labels use four categories: `status:`, `phase:`, `type:`, `priority:`
- The active issue is stored in `.claude/session.json` → `active_task.github_issue`

## Owner / Repo

Read from `.claude/harness.json` → `github.owner` and `github.repo`.
```

---

### Task 3: Create issue-tracker-github-projects.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/issue-tracker-github-projects.md`

- [ ] **Step 1: Write issue-tracker-github-projects.md**

```markdown
# Issue Tracker: GitHub Projects v2

## Commands

```bash
# Create issue (issue → board automatically via label-based automation)
gh issue create --title "type: description" --body "..." --label "status:triage,phase:execution"

# List ready issues for current phase
gh issue list --label "status:ready-for-agent,phase:execution"

# View issue
gh issue view <N>

# Update label (board column moves automatically)
gh issue edit <N> --add-label "status:in-progress" --remove-label "status:ready-for-agent"

# Add comment
gh issue comment <N> --body "..."
```

## Board columns

| Column | Status label |
|---|---|
| Triage | `status:triage` |
| Needs PRD | `status:needs-prd` |
| Needs Review | `status:needs-review` |
| Ready for Agent | `status:ready-for-agent` |
| In Progress | `status:in-progress` |
| Done | `status:done` |

Column tracks `status:` label. When label changes, item moves automatically.

## Config

- Board ID: read from `.claude/harness.json` → `github.project_v2_id`
- Board name: read from `.claude/harness.json` → `github.project_board_name`
- Active issue: `.claude/session.json` → `active_task.github_issue`
- Active item ID: `.claude/session.json` → `active_task.github_project_item_id`
```

---

### Task 4: Create triage-labels.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/triage-labels.md`

- [ ] **Step 1: Write triage-labels.md**

```markdown
# Triage Labels

## Status labels

| Label | Meaning |
|---|---|
| `status:triage` | New issue — not yet assessed |
| `status:needs-prd` | Needs a PRD before stories can be written |
| `status:needs-review` | HITL: written but agent lacks confidence in ≥1 AC item — human must validate before execution |
| `status:needs-info` | Blocked on missing information from stakeholder |
| `status:ready-for-agent` | AFK: all AC traceable to cited sources, chain complete — agent can execute |
| `status:in-progress` | Agent is actively working on this issue |
| `status:done` | All AC pass, PR merged |
| `status:wontfix` | Closed without implementation |
| `status:ready-for-human` | Needs human action (code review, design decision) |

## Phase labels

| Label | Meaning |
|---|---|
| `phase:design` | Design phase work (spec, ADR, discovery) |
| `phase:product` | Product phase work (PRD, story breakdown) |
| `phase:execution` | Execution phase work (implementation) |
| `phase:testing` | Testing phase work (QA, issue filing) |

## Type labels

| Label | Meaning |
|---|---|
| `type:feature` | New user-facing capability |
| `type:bug` | Defect in existing functionality |
| `type:chore` | Non-functional maintenance (deps, config, cleanup) |
| `type:task` | Internal task with no direct user impact |
| `type:spike` | Throwaway investigation — 1 context window, AFK, discarded after decision is made |

## Priority labels

| Label | Meaning |
|---|---|
| `priority:p1` | Must fix before release |
| `priority:p2` | Important but not blocking |
| `priority:p3` | Nice to have |

## Status flow

```
triage → needs-prd → [needs-review | ready-for-agent] → in-progress → done
```

- `needs-review`: HITL. Human validates AC sources, then relabels to `ready-for-agent`.
- `ready-for-agent`: AFK (agent confident) or human-approved from `needs-review`.
```

---

### Task 5: Create domain.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/domain.md`

- [ ] **Step 1: Write domain.md**

```markdown
# Domain Context

<!-- This file provides domain terminology and context for harness skills.
     Edit it after setup to reflect your project's specific language and concepts.
     The canonical term glossary lives in CONTEXT.md — this file is the harness
     agent's operating context, not a replacement for it. -->

## Project

**Name:** [your project name]
**Domain:** [e.g., e-commerce, SaaS, developer tooling, internal platform]
**Primary users:** [e.g., software engineers, end customers, operations team]

## Key concepts

<!-- Add domain-specific terms that AI agents need to understand.
     Format: **Term**: one-sentence definition.
     Only include terms unique to this domain — skip general programming concepts. -->

## External integrations

<!-- List APIs, services, and third-party systems the project integrates with.
     Format: **Service**: what it does in this project. -->

## Constraints

<!-- List regulatory, compliance, or architectural constraints that affect all decisions.
     These are the non-negotiables that every agent session must respect. -->
```

---

### Task 6: Create github-project.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/github-project.md`

- [ ] **Step 1: Write github-project.md**

```markdown
# GitHub Project Board

**Board ID:** [written by /setup-harness-skills from harness.json — do not edit manually]
**Board name:** [written by /setup-harness-skills]

## Columns

| Column | Status label | Who moves here | Human action? |
|---|---|---|---|
| Triage | `status:triage` | Agent | No |
| Needs PRD | `status:needs-prd` | Agent | No |
| Needs Review | `status:needs-review` | Agent (HITL stories) | **Yes — human validates AC + sources** |
| Ready for Agent | `status:ready-for-agent` | Human (from Needs Review) or Agent (AFK) | Triggers execution |
| In Progress | `status:in-progress` | Agent (`/session-start`) | No |
| Done | `status:done` | GitHub (PR merged) | **Yes — human merges PR** |

## Custom fields

- **Effort (windows):** number field — Product-phase agent's estimate of context windows to complete the issue. Execution agent updates if actual effort differs significantly.

## Human gates

1. **Needs Review → Ready for Agent:** Human validates AC sources and confidence declaration for HITL stories. This is the Product phase exit gate — no issue moves to execution until human approves.
2. **In Progress → Done:** Human merges the PR. Branch protection enforces this gate — direct pushes to main are blocked.

## Phase exit oracles

| Phase | Oracle |
|---|---|
| Design | Design Phase Tracking Issue has label `design-approved` or is closed by human |
| Product | All `phase:execution` issues have `status:ready-for-agent` (none remain in `needs-review`) |
| Execution | All `phase:execution` issues are closed via merged PRs |
| Testing | All `phase:testing` issues are `status:done`; no open `priority:p1` bugs remain |
```

---

### Task 7: Create session-config.md

**Files:**
- Create: `skills/engineering/setup-harness-skills/session-config.md`

- [ ] **Step 1: Write session-config.md**

````markdown
# Session Configuration

## session.json schema

**Location:** `.claude/session.json` (gitignored — project-local only, never committed)

```json
{
  "schema_version": 1,
  "current_phase": "execution",
  "active_task": {
    "github_issue": 42,
    "title": "Implement auth middleware",
    "effort_estimate": 1,
    "github_project_item_id": "PVI_xxxx"
  },
  "last_handover": "2026-05-24T10:30:00Z",
  "next_session_hint": "Continue from UserService.login() — happy path done, need sad path + tests"
}
```

## Fields

| Field | Type | Description |
|---|---|---|
| `schema_version` | number | Always `1` in this version |
| `current_phase` | string | One of: `design`, `product`, `execution`, `testing` |
| `active_task.github_issue` | number \| null | GitHub issue number (`null` if using local markdown) |
| `active_task.title` | string | Issue title — human-readable reference |
| `active_task.effort_estimate` | number | Context windows estimated remaining for this issue |
| `active_task.github_project_item_id` | string \| null | Project v2 item ID (`null` if no board configured) |
| `last_handover` | ISO 8601 | Timestamp of last `/context-handover` run |
| `next_session_hint` | string | Free-text pickup point written by `/context-handover` |

## Written by

- `session-start` — initializes on first run or after phase transition
- `context-handover` — updates `last_handover`, `next_session_hint`, phase transitions

## Read by

- `session-start` — determines active phase and task for session briefing
- `context-handover` — reads current phase for handoff doc and GitHub comment
- `harness-engineering` — checks for setup as part of gap detection

## harness.json schema

**Location:** `.claude/harness.json` (committed — shared team config, analogous to package.json)

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

Written by: `setup-harness-skills`.
Read by: `session-start`, `context-handover`, `harness-engineering`, `to-issues`.
````

- [ ] **Step 2: Commit all seed templates**

```bash
git add skills/engineering/setup-harness-skills/
git commit -m "feat(setup-harness-skills): add 6 bundled seed templates"
```

---

## Chunk 3: Evals and Plugin Registration

### Task 8: Create evals/evals.json

**Files:**
- Create: `skills/engineering/setup-harness-skills/evals/evals.json`

- [ ] **Step 1: Write evals.json**

```json
{
  "evals": [
    {
      "id": 1,
      "prompt": "I'm starting a new Next.js project and want to use harness skills. Please set up the harness.",
      "files": [
        "package.json with next.js",
        "CLAUDE.md"
      ],
      "expectations": [
        "Explores project state first (reads .git/config, existing instruction files, docs/agents/) before asking any questions",
        "Presents a one-line summary of what it found before proceeding to questions",
        "Asks about the issue tracker before asking about labels or domain docs (Section A comes first)",
        "Does NOT ask all questions at once — questions are asked one section at a time",
        "Mentions writing docs/agents/ seed files as part of the output steps",
        "Mentions writing to CLAUDE.md (not AGENTS.md) because CLAUDE.md already exists",
        "Does NOT propose creating AGENTS.md when CLAUDE.md exists"
      ]
    },
    {
      "id": 2,
      "prompt": "I want to update the harness setup. I already ran setup before — docs/agents/ exists with config files.",
      "files": [
        "package.json",
        "CLAUDE.md",
        "docs/agents/issue-tracker.md with github issues config",
        "docs/agents/triage-labels.md"
      ],
      "expectations": [
        "Detects existing docs/agents/ config files during the explore step and notes them explicitly",
        "Does not overwrite existing config with blank defaults without confirming",
        "References the existing issue tracker config rather than re-asking from scratch"
      ]
    },
    {
      "id": 3,
      "prompt": "Set up harness skills for this project. There is no CLAUDE.md or AGENTS.md yet.",
      "files": [
        "package.json"
      ],
      "expectations": [
        "Detects that neither CLAUDE.md nor AGENTS.md exists during the explore step",
        "Asks the user which instruction file to create (CLAUDE.md or AGENTS.md) — presents both options",
        "Does NOT make the choice unilaterally or default to one without asking"
      ]
    }
  ]
}
```

- [ ] **Step 2: Verify evals.json is valid JSON**

```bash
python -c "import json; json.load(open('skills/engineering/setup-harness-skills/evals/evals.json'))" && echo "OK: evals.json valid"
```
Expected: `OK: evals.json valid`

---

### Task 9: Update plugin.json and engineering README

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `skills/engineering/README.md`

- [ ] **Step 1: Add setup-harness-skills to plugin.json**

In `.claude-plugin/plugin.json`, change the `"skills"` array from:
```json
"skills": [
  "skills/engineering/harness-engineering"
]
```
to:
```json
"skills": [
  "skills/engineering/harness-engineering",
  "skills/engineering/setup-harness-skills"
]
```

- [ ] **Step 2: Verify plugin.json is still valid JSON**

```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json'))" && echo "OK: plugin.json valid"
```

- [ ] **Step 3: Update skills/engineering/README.md status for setup-harness-skills**

Change:
```
| `setup-harness-skills` | One-time gateway: configure GitHub, labels, session state | Plan 2 |
```
to:
```
| `setup-harness-skills` | One-time gateway: configure GitHub, labels, session state | Implemented |
```

- [ ] **Step 4: Commit chunk 3**

```bash
git add skills/engineering/setup-harness-skills/evals/ .claude-plugin/plugin.json skills/engineering/README.md
git commit -m "feat(setup-harness-skills): add evals, register in plugin.json"
```

---

## Chunk 4: Verification

### Task 10: Final checks

- [ ] **Step 1: Verify skill directory structure**

```bash
find skills/engineering/setup-harness-skills -type f | sort
```
Expected files:
```
skills/engineering/setup-harness-skills/SKILL.md
skills/engineering/setup-harness-skills/domain.md
skills/engineering/setup-harness-skills/evals/evals.json
skills/engineering/setup-harness-skills/github-project.md
skills/engineering/setup-harness-skills/issue-tracker-github-projects.md
skills/engineering/setup-harness-skills/issue-tracker-github.md
skills/engineering/setup-harness-skills/session-config.md
skills/engineering/setup-harness-skills/triage-labels.md
```

- [ ] **Step 2: Verify list-skills shows both skills**

```bash
bash scripts/list-skills.sh
```
Expected:
```
SKILL                          PATH
-----                          ----
harness-engineering            skills/engineering/harness-engineering
setup-harness-skills           skills/engineering/setup-harness-skills
```

- [ ] **Step 3: Verify git log shows the three plan commits**

```bash
git log --oneline -5
```
Expected (newest first):
```
<hash> feat(setup-harness-skills): add evals, register in plugin.json
<hash> feat(setup-harness-skills): add 6 bundled seed templates
<hash> feat(setup-harness-skills): add SKILL.md with 5-section interaction flow
```

- [ ] **Step 4: Verify git status is clean**

```bash
git status
```
Expected: `nothing to commit, working tree clean`

---

**Plan 2 complete.**

**Next:** Plan 3 — `context-handover` + `session-start`. Read spec Sections 5.2 and 5.3 at the start of the next execution session.

**Spec reference:** `docs/superpowers/specs/2026-05-24-harness-skill-collection-design.md` — Sections 5.2, 5.3, 5.4, 5.5, 5.6.
