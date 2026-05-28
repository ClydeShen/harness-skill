# Session Configuration

## state.json schema

**Location:** `.planning/state.json` (committed — shared across sessions and agents)

```json
{
  "version": "1.0",
  "session": {
    "status": "idle",
    "started_at": "ISO 8601",
    "last_active": "ISO 8601",
    "last_session": "ISO 8601"
  },
  "position": {
    "phase": "01-discuss",
    "active_task": "task title string",
    "resume_file": ".planning/phases/01-discuss/.continue-here.json",
    "stopped_at": "brief description of last action"
  }
}
```

## Fields

| Field | Type | Written by | Description |
|---|---|---|---|
| `version` | string | setup-harness-skills | Schema version — never change manually |
| `session.status` | `"idle"` \| `"in_progress"` | SessionStart hook | State machine marker |
| `session.started_at` | ISO 8601 | SessionStart hook | When current session began |
| `session.last_active` | ISO 8601 | Stop hook | Updated every Claude turn — staleness = true interruption |
| `session.last_session` | ISO 8601 | context-handover | When last clean handover ran |
| `position.phase` | string | context-handover | Directory name: `01-discuss`, `02-plan`, `03-execute`, `04-verify` |
| `position.active_task` | string | session-start / context-handover | Human-readable task title |
| `position.resume_file` | string | context-handover | Path to `.continue-here.json` |
| `position.stopped_at` | string | context-handover | One-line description of last action |

## Interruption detection

`session.status == "in_progress"` AND `session.last_active` is >5 minutes old → interrupted session.

Using `last_active` (not `started_at`) eliminates false positives on long active sessions. The Stop hook fires after every Claude response, so `last_active` only goes stale when the session was truly cut off.

## Written by

- `SessionStart hook` — status → in_progress, started_at → now (automatic, no agent step required)
- `Stop hook` — last_active → now (every turn, automatic)
- `context-handover` — status → idle, last_session, position fields (agent-driven full save)
- `session-start` — position.active_task if user provides context at start

## Read by

- `SessionStart hook` — outputs current state as additionalContext into Claude's context window
- `session-start` — briefing generation, phase skip/revert evaluation
- `context-handover` — phase detection, resume_file path resolution
- `harness-audit` — checks for setup as part of gap detection

## .continue-here.json schema

**Location:** `.planning/phases/XX-name/.continue-here.json` (gitignored — ephemeral per session)

```json
{
  "version": "1.0",
  "phase": "01-discuss",
  "task": 1,
  "total_tasks": 3,
  "status": "in_progress",
  "last_updated": "ISO 8601",
  "current_state": "...",
  "completed_work": ["..."],
  "remaining_work": ["..."],
  "decisions_made": ["..."],
  "blockers": [],
  "context": "...",
  "next_action": "Start with: ..."
}
```

Written by: `context-handover`. Read by: `session-start`. Validated by: PostToolUse hook.

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

Written by: `setup-harness-skills`. Read by: `session-start`, `context-handover`, `harness-audit`, `to-issues`.
