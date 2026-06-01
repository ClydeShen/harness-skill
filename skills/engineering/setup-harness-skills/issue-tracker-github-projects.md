# Issue Tracker: GitHub Projects v2

## Commands

```bash
# Create issue (auto-added to board via project-auto-add.yml workflow — requires PROJECT_TOKEN secret)
gh issue create --title "type: description" --body "..." --label "status:triage,phase:execution"

# List ready issues for current phase
gh issue list --label "status:ready-for-agent,phase:execution"

# View issue
gh issue view <N>

# Update label (board column syncs via project-sync-status.yml workflow — requires PROJECT_TOKEN secret)
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

**Column sync is NOT automatic.** GitHub Projects v2 does not bridge `status:` labels to the board Status field on its own. Two GitHub Actions workflows (written by Step 5b of `setup-harness-skills`) provide this:

- `project-auto-add.yml` — adds every new issue to the board automatically
- `project-sync-status.yml` — watches `issues: labeled` events and updates the board Status field to match the `status:` label

Both workflows require a repository secret `PROJECT_TOKEN` (Classic PAT with `repo` + `project` scopes). Without it, column sync silently fails.

## Config

- Board ID: read from `.claude/harness.json` → `github.project_v2_id`
- Board name: read from `.claude/harness.json` → `github.project_board_name`
- Active issue: `.harness/state.json` → `position.active_task` (title); issue number from GitHub issue body
- Active item ID: `.claude/harness.json` → `github.project_v2_id` (board-level; item ID resolved via GraphQL)
