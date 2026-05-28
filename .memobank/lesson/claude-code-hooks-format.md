---
name: claude-code-hooks-format
type: lesson
description: Claude Code settings.json hooks require string matcher and "command" type — "prompt" type does not exist
tags:
  - hooks
  - claude-code
  - harness-audit
status: active
created: 2026-05-26
---

# Claude Code Hooks Format

The correct schema for `.claude/settings.json` hooks:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "echo 'your reminder text'"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "echo 'your reminder text'"}]
      }
    ]
  }
}
```

**Two non-obvious traps (both triggered during onboarding of this repo):**

1. `matcher` must be a **plain string** (`"Write"`, `"Edit|Write"`, or `""` for all). Writing `{"type": "Write"}` as an object passes silently but fails `/doctor`.
2. Hook `type` must be `"command"` — `"prompt"` is not a valid type. Use `echo` to inject reminder text; Claude Code feeds stdout back to the model.

**Why it matters:** The `harness-audit` skill outputs paste-ready snippets. If those snippets use the wrong format, every project onboarded via this skill inherits broken hooks — `/doctor` reports errors but the hooks silently do nothing.

**Fixed in:** commit `f7cfa84` — `SKILL.md` paste-ready snippet, `references/universal-snippets.md`, and `.claude/settings.json` all corrected. Eval `#16` added to prevent regression.
