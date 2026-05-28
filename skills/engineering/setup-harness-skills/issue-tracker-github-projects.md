# Issue Tracker: GitHub Projects v2

## Commands

```bash
# Create issue (automatically added to board via label-based automation)
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
- Active issue: `.planning/state.json` → `position.active_task` (title); issue number from GitHub issue body
- Active item ID: `.claude/harness.json` → `github.project_v2_id` (board-level; item ID resolved via GraphQL)
