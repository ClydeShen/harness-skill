#!/usr/bin/env bash
# PostToolUse hook (matcher: Write|Edit) — validate state.json after writes.
#
# Reads tool input from stdin. If the written file is state.json or
# .continue-here.json, validates it is well-formed JSON and contains
# required top-level keys. Emits a warning via additionalContext if invalid.
#
# Requires: jq

command -v jq >/dev/null 2>&1 || exit 0

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)

case "$FILE" in
  *state.json)
    if ! jq -e '.version and .session and .position' "$FILE" >/dev/null 2>&1; then
      jq -n '{
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          additionalContext: "WARNING: state.json is missing required fields (version, session, position). Fix before next /session-start."
        }
      }'
    fi
    ;;
  *.continue-here.json)
    if ! jq -e '.version and .phase and .next_action' "$FILE" >/dev/null 2>&1; then
      jq -n '{
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          additionalContext: "WARNING: .continue-here.json is missing required fields (version, phase, next_action)."
        }
      }'
    fi
    ;;
esac

exit 0
