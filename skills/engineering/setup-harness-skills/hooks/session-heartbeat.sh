#!/usr/bin/env bash
# Stop hook — update last_active timestamp on every Claude turn.
#
# Provides accurate interruption detection: last_active going stale (>5 min)
# means the session was truly interrupted, not just a long active session.
#
# Requires: jq
# No-op if state.json absent or session is not in_progress.

STATE=".planning/state.json"
if [ ! -f "$STATE" ]; then exit 0; fi

command -v jq >/dev/null 2>&1 || exit 0

STATUS=$(jq -r '.session.status // ""' "$STATE" 2>/dev/null)
if [ "$STATUS" != "in_progress" ]; then exit 0; fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TMP=$(mktemp)
jq --arg ts "$NOW" '.session.last_active = $ts' "$STATE" > "$TMP" && mv "$TMP" "$STATE"

exit 0
