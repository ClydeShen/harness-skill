# Output Steps

Execute in order after all five sections are confirmed.

## Step 1 — Instruction file (CLAUDE.md / AGENTS.md)

**If CLAUDE.md or AGENTS.md already exists:** skip this step entirely. Do not modify the file.

**If neither exists** (Section A.5 was triggered and user chose a file):

Show the full draft below and confirm before writing. Use `CLAUDE.md` or `AGENTS.md` per the user's Section A.5 answer.

```markdown
# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
    3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Harness Discipline

**Long-running work fails silently. Epistemic gaps compound into errors. Make both kinds of boundary explicit.**

- Don't fabricate. Every factual claim must trace to observed evidence, documentation, or established best practice. Confidence is not a source — if you cannot ground a claim, say so rather than presenting it as fact.
- It's OK not to know. Say so explicitly instead of guessing. Proactively surface information gaps and ask what you need to proceed — don't fill them with plausible-sounding assumptions.
- While implementing a spec, maintain a running `.harness/implementation-notes.md` capturing: decisions made that weren't covered by the spec, things that had to change from the original plan, tradeoffs you made, and anything else the human should know.
- Exit criteria must be observable: a gate that passed, not a feeling that it's done. Name the anti-patterns: Fuzzy Done, Proxy Signal, Confidence Exit.
- State lives outside the agent. The source of truth is the issue tracker, the handoff document, the config file — not working memory.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, clarifying questions come before implementation rather than after mistakes, and long-running sessions hand off cleanly without lost context.
```

- Record in summary: `✅ CLAUDE.md written` (or AGENTS.md).

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

1. Create board and add `Effort (windows)` number field:
   ```bash
   PROJECT_NUMBER=$(gh project create --owner "$OWNER" --title "$BOARD_NAME" --format json --jq '.number')
   gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
     --name "Effort (windows)" --data-type "NUMBER"
   ```

2. Create `Priority` and `Size` single-select fields if not already present (idempotent — check existing fields first):
   ```bash
   # Check existing fields before creating
   EXISTING=$(gh project field-list $PROJECT_NUMBER --owner "$OWNER" --format json --jq '[.fields[].name]')

   # Create Priority if absent
   echo "$EXISTING" | grep -q '"Priority"' || \
     gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
       --name "Priority" --data-type "SINGLE_SELECT" \
       --single-select-options "P1,P2,P3"

   # Create Size if absent
   echo "$EXISTING" | grep -q '"Size"' || \
     gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
       --name "Size" --data-type "SINGLE_SELECT" \
       --single-select-options "XS,S,M,L,XL"
   ```

3. Query field metadata to capture IDs and option maps:
   ```bash
   PROJECT_ID=$(gh project view $PROJECT_NUMBER --owner "$OWNER" --format json --jq '.id')

   gh api graphql -f query='
   query($board: ID!) {
     node(id: $board) {
       ... on ProjectV2 {
         fields(first: 20) {
           nodes {
             ... on ProjectV2SingleSelectField { id name options { id name } }
             ... on ProjectV2Field { id name dataType }
           }
         }
       }
     }
   }' -f board="$PROJECT_ID"
   ```

   Map results:
   - Field named `Priority` → `project_fields.priority` (`id` + `options` map `{P1: <id>, P2: <id>, P3: <id>}`)
   - Field named `Size` → `project_fields.size` (`id` + `options` map `{XS: <id>, S: <id>, M: <id>, L: <id>, XL: <id>}`)
   - Field named `Effort (windows)` → `project_fields.effort` (`id` only)
   - Skip any field not found (partial population is valid).

4. Merge `project_fields` key into `.claude/harness.json` (idempotent — merge over existing values; never overwrite keys already present):
   ```json
   {
     "project_fields": {
       "priority": {
         "id": "<PVTSSF_... from board>",
         "options": { "P1": "<option-id>", "P2": "<option-id>", "P3": "<option-id>" }
       },
       "size": {
         "id": "<PVTSSF_... from board>",
         "options": {
           "XS": "<option-id>",
           "S":  "<option-id>",
           "M":  "<option-id>",
           "L":  "<option-id>",
           "XL": "<option-id>"
         }
       },
       "effort": {
         "id": "<PVTF_... from board>"
       }
     }
   }
   ```

5. Write `project_v2_id`, `project_board_name`, and `project_number` back to `harness.json`.

**Graceful degradation:** If the board has no Priority/Size/Effort (windows) fields, omit the corresponding sub-key. Downstream skills check for key presence before calling mutations.

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
✅ CLAUDE.md written
✅ .claude/harness.json written
✅ GitHub labels created (N labels)
✅ docs/agents/ seed files written
✅ .harness/settings.json written (model: claude-sonnet-4, 1M context)
⚠️ Branch protection: requires admin:repo permission — set manually
📁 Files written: docs/agents/issue-tracker.md, triage-labels.md, domain.md, github-project.md, session-config.md, .harness/settings.json
```
