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
- The active issue title is stored in `.harness/state.json` → `position.active_task`

## Owner / Repo

Read from `.harness/config.json` → `harness.github.owner` and `harness.github.repo`.
