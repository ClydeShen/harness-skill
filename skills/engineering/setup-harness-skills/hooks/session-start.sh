#!/usr/bin/env bash
# SessionStart hook — transition state to in_progress and inject context into Claude.
#
# Reads .planning/state.json, atomically sets session.status = "in_progress"
# and session.started_at = now, then emits the current position as
# additionalContext so Claude receives state without reading files.
#
# Requires: jq
# No-op if .planning/state.json absent (cold start).

STATE=".planning/state.json"
if [ ! -f "$STATE" ]; then exit 0; fi

command -v jq >/dev/null 2>&1 || { echo '{}'; exit 0; }

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Atomic update: read → mutate → rename
TMP=$(mktemp)
jq --arg ts "$NOW" '
  .session.status = "in_progress" |
  .session.started_at = $ts
' "$STATE" > "$TMP" && mv "$TMP" "$STATE"

# Read fields for additionalContext
PHASE=$(jq -r '.position.phase // "unknown"' "$STATE")
TASK=$(jq -r '.position.active_task // "none"' "$STATE")
RESUME=$(jq -r '.position.resume_file // ""' "$STATE")
STOPPED=$(jq -r '.position.stopped_at // ""' "$STATE")
LAST_SESSION=$(jq -r '.session.last_session // ""' "$STATE")

# Emit additionalContext — injected into Claude's context window at session start
jq -n \
  --arg phase "$PHASE" \
  --arg task "$TASK" \
  --arg resume "$RESUME" \
  --arg stopped "$STOPPED" \
  --arg last_session "$LAST_SESSION" \
  '{
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: (
        "## Harness Session State\n" +
        "Phase: " + $phase + "\n" +
        "Active task: " + $task + "\n" +
        (if $resume != "" then "Resume file: " + $resume + "\n" else "" end) +
        (if $stopped != "" then "Stopped at: " + $stopped + "\n" else "" end) +
        (if $last_session != "" then "Last session: " + $last_session + "\n" else "" end) +
        "\nRun /session-start to get the full briefing."
      )
    }
  }'

exit 0
