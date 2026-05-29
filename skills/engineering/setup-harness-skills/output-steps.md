# Output Steps

Execute in order after all five sections are confirmed.

## Step 1 — `## Agent skills` block

Show draft before writing:
- If block already exists in CLAUDE.md / AGENTS.md: show diff (old → new)
- If not found: show new block and confirm append location

Write to whichever of CLAUDE.md / AGENTS.md exists — never create the other.
Idempotent: replace existing block in-place, never append a second copy.

## Step 2 — Write `.claude/harness.json`

Merge over existing values if file already exists:

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

## Step 3 — Create GitHub labels

Skip any label that already exists (idempotent):

```bash
# Status
gh label create "status:triage" --color "#e4e669"
gh label create "status:needs-prd" --color "#d4c5f9"
gh label create "status:needs-review" --color "#f9c846"
gh label create "status:needs-info" --color "#f9c846"
gh label create "status:ready-for-agent" --color "#0075ca"
gh label create "status:in-progress" --color "#e99695"
gh label create "status:done" --color "#0e8a16"
gh label create "status:wontfix" --color "#ffffff"
gh label create "status:ready-for-human" --color "#cfd3d7"

# Phase
gh label create "phase:design" --color "#c2e0c6"
gh label create "phase:product" --color "#bfd4f2"
gh label create "phase:execution" --color "#fef2c0"
gh label create "phase:testing" --color "#f9d0c4"

# Type
gh label create "type:feature" --color "#84b6eb"
gh label create "type:bug" --color "#ee0701"
gh label create "type:chore" --color "#e4e669"
gh label create "type:task" --color "#bfd4f2"
gh label create "type:spike" --color "#d4c5f9"

# Priority
gh label create "priority:p1" --color "#b60205"
gh label create "priority:p2" --color "#e4e669"
gh label create "priority:p3" --color "#cfd3d7"
```

`status:needs-review` is required — it is the plan phase exit human gate.

## Step 4 — Create GitHub Milestones

Only if user provided names in Section D. Skip any that already exist:

```bash
gh api repos/{owner}/{repo}/milestones --method POST --field title="Design"
gh api repos/{owner}/{repo}/milestones --method POST --field title="MVP"
gh api repos/{owner}/{repo}/milestones --method POST --field title="v1.0"
```

## Step 5 — Create GitHub Project v2 board

Only if user opted in during Section D:
- Create board via `gh project create`
- Add `Effort (windows)` number field
- Write `project_v2_id` and `project_board_name` back to `harness.json`

## Step 6 — Configure branch protection

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field enforce_admins=true \
  --field 'required_status_checks={"strict":true,"contexts":["ci"]}' \
  --field 'required_pull_request_reviews={"required_approving_review_count":0}' \
  --field restrictions=null
```

If this fails (insufficient permissions): record as "Requires manual action" in setup summary. Continue other steps.

## Step 7 — Scaffold `.github/workflows/ci.yml`

**Idempotency guard:** Before writing, check for any `*.yml` in `.github/workflows/`. If any exist, skip this step and record in the setup summary:

```
⚠️ CI scaffold skipped — existing workflows found
```

**When no workflows exist:** Write a minimal stack-agnostic placeholder:

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # TODO: add your build/test steps here
```

Record in the setup summary: `✅ .github/workflows/ci.yml written (placeholder — customize for your stack)`

## Step 7a — Write harness issue templates to `.github/ISSUE_TEMPLATE/`

Copy from this skill's `github-issue-templates/` folder to `.github/ISSUE_TEMPLATE/` in the target project.

Idempotent: skip any file that already exists at the destination.

Files to copy:
- `github-issue-templates/harness-issue.md` → `.github/ISSUE_TEMPLATE/harness-issue.md`
- `github-issue-templates/bug-report.md` → `.github/ISSUE_TEMPLATE/bug-report.md`

Record in the setup summary:
```
✅ .github/ISSUE_TEMPLATE/harness-issue.md written
✅ .github/ISSUE_TEMPLATE/bug-report.md written
```

## Step 8 — Write `.claude/hooks/` and configure `.claude/settings.json`

Copy the three hook templates from this skill's `hooks/` folder to the user's project:

```
.claude/hooks/session-start.sh      ← SessionStart: state transition + additionalContext inject
.claude/hooks/session-heartbeat.sh  ← Stop: update last_active every turn
.claude/hooks/validate-state.sh     ← PostToolUse: validate state.json / .continue-here.json
```

Make executable:
```bash
chmod +x .claude/hooks/session-start.sh .claude/hooks/session-heartbeat.sh .claude/hooks/validate-state.sh
```

Merge into `.claude/settings.json` (idempotent — only add missing entries):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "bash .claude/hooks/session-start.sh" }]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "bash .claude/hooks/session-heartbeat.sh" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "bash .claude/hooks/validate-state.sh" }]
      }
    ]
  }
}
```

**Dependency check:** hooks require `jq`. If absent, note in setup summary:
> "`jq` not found — install with `brew install jq` (macOS) or `apt install jq` (Linux). Hooks will silently no-op until installed."

## Step 8a — Append to `.gitignore`

Idempotent — skip lines already present:

```
.claude/handoff.md
.harness/phases/*/.continue-here.json
```

`.claude/harness.json` and `.harness/state.json` are NOT gitignored — committed as shared team config.

## Step 9 — Write seed files to `docs/agents/`

Copy from bundled templates in this skill's folder:

```
docs/agents/issue-tracker.md    ← issue-tracker-github.md or issue-tracker-github-projects.md
docs/agents/triage-labels.md    ← triage-labels.md
docs/agents/domain.md           ← domain.md
docs/agents/github-project.md   ← github-project.md
docs/agents/session-config.md   ← session-config.md
```

## Step 10 — Write `.harness/settings.json`

Always write — this file is consumed by `context-handover` for session budget planning and by `harness-audit` for model-aware gap detection.

```json
{
  "version": "1.0",
  "model": {
    "type": "claude-sonnet

```
✅ ## Agent skills block written to CLAUDE.md
✅ .claude/harness.json written
✅ GitHub labels created (N labels)
✅ docs/agents/ seed files written
✅ .harness/settings.json written (model: claude-sonnet-4, 1M context)
⚠️ Branch protection: requires admin:repo permission — set manually
📁 Files written: docs/agents/issue-tracker.md, triage-labels.md, domain.md, github-project.md, session-config.md, .harness/settings.json
```
