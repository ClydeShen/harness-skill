# Issue Tracker

**Platform:** GitHub Issues
**CLI:** `gh issue`
**Repo:** ClydeShen/harness-skill

## Usage

```bash
# Create
gh issue create --title "..." --body "..." --label "status:needs-triage"

# List
gh issue list

# View
gh issue view <number>

# Close
gh issue close <number>

# Add label
gh issue edit <number> --add-label "status:ready-for-agent"
```
