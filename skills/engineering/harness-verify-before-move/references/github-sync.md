# GitHub Project Sync

Loaded by `harness-verify-before-move` Step 7. Skip this file if `docs/agents/issue-tracker.md` does not exist.

## Config lookup (in order)

1. `.harness/config.json` → `github.owner`, `github.repo`, `github.project_id`, `github.milestone`
2. `docs/agents/issue-tracker.md` — parse the same fields
3. If neither found: output "GitHub config not found — run `/setup-harness-skills`" and skip all steps below

---

## 1. Milestone sync

```bash
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | {title, open_issues, closed_issues, due_on, state}'
```

Check:
- Active milestone exists with a `due_on` date
- `% complete = closed_issues / (open_issues + closed_issues)` — report this number
- Flag if milestone has 0 closed issues (stale or newly created — ask user to confirm)
- Flag if milestone is overdue (`due_on` < today) and still `open`

Output: `Milestone "[name]": N% complete (N closed / N open) | due YYYY-MM-DD`

---

## 2. Issue status labels

```bash
gh issue list --repo {owner}/{repo} --milestone "{milestone}" \
  --state all --json number,title,state,labels,updatedAt
```

Rules:
- Every open issue must have exactly **one** `status:*` label
- A closed issue must not have `status:in-progress` or `status:ready-for-agent`
- An issue with a merged PR linked must be closed (or explicitly kept open with a comment)

Corrections to flag (do not apply without user approval):
```
CORRECTION: #N "[title]"
  Current: status:in-progress (issue is closed)
  Proposed: remove status label
  Command: gh issue edit N --remove-label "status:in-progress" --repo {owner}/{repo}
```

---

## 3. Project board sync

Query board column positions via GraphQL:

```bash
gh api graphql -f query='
{
  node(id: "{project_id}") {
    ... on ProjectV2 {
      items(first: 50) {
        nodes {
          content { ... on Issue { number title state } }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
        }
      }
    }
  }
}'
```

Expected column alignment:

| Issue state | Status label | Expected column |
|---|---|---|
| open | `status:triage` | Triage |
| open | `status:needs-prd` | Needs PRD |
| open | `status:needs-review` | Needs Review |
| open | `status:ready-for-agent` | Ready for Agent |
| open | `status:in-progress` | In Progress |
| closed | any | Done |

Flag each mismatch. Propose `gh` move command. Run only on approval.

---

## 4. Stale issue detection

Issues with `updatedAt` > 7 days ago and no `status:blocked` or `status:on-hold` label are stale candidates.

```bash
gh issue list --repo {owner}/{repo} --state open \
  --json number,title,updatedAt,labels \
  | jq '[.[] | select(.updatedAt < (now - 604800 | todate))]'
```

Output as a list. Do not close. User decides next action.

---

## 5. Linked PR check

```bash
gh pr list --repo {owner}/{repo} --state open \
  --json number,title,isDraft,closingIssuesReferences
```

Flag:
- **Draft PRs** linked to issues being closed this phase → "PR still in draft — cannot close issue yet"
- **Merged PRs** whose linked issues are still open → propose `gh issue close N --repo {owner}/{repo}`

Output as one-line warnings. Run no commands without approval.

---

## Output format for Step 7

```
GitHub sync
  Milestone: "[name]" — N% complete (N/N) | due YYYY-MM-DD   [OK / OVERDUE]
  Issues: N checked | N label corrections proposed
  Board: N column moves proposed
  Stale: N issues flagged (no activity >7 days)
  PRs: N draft linked | N merged/open linked

[list proposed corrections and commands]
Approve corrections? (y/n per item or y/all)
```
