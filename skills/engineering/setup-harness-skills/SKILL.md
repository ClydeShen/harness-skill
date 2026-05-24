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

Accept the defaults (user says "yes" or "looks good") or wait for overrides. Note any overrides before proceeding to Section C.

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
docs/agents/issue-tracker.md    ← issue-tracker-github.md or issue-tracker-github-projects.md
docs/agents/triage-labels.md    ← triage-labels.md
docs/agents/domain.md           ← domain.md
docs/agents/github-project.md   ← github-project.md
docs/agents/session-config.md   ← session-config.md
```

After all steps, print a **setup summary**:
- ✅ Items completed
- ⚠️ Items requiring manual action (e.g., branch protection, unknown stack)
- 📁 Files written to `docs/agents/`

Then: "Run `/session-start` to begin your first session."

---

_🤖 All comments and issue bodies posted by this skill end with this footer._
