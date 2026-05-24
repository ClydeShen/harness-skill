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
