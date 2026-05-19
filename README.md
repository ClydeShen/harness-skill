# harness-engineering skill

A Claude Code skill that detects agent-harness gaps in a project and produces paste-ready config snippets to close them.

## What it does

When invoked, the skill runs in three phases:

1. **Detect** — scans the project for missing harness components (hooks, CI, pre-commit, CLAUDE.md quality, init script, spec workflow)
2. **Interview** — asks at most 3 targeted questions to resolve what the file scan cannot determine (task scope, team size, priority)
3. **Output** — produces a prioritised gap list with complete, paste-ready snippets for the top 5 gaps

## When to use it

Trigger phrases (the skill description routes automatically):

- "start session", "set up harness", "session start"
- "set up quality gates", "CI pipeline", "pre-commit hooks"
- "what do I need before I start", "how do I keep claude on track"
- "writing CLAUDE.md", "goal structure", "sprint contract", "verification gap"

Any session-start or task-structure question qualifies — even without the word "harness".

## Skill structure

```
skills/harness-engineering/
  SKILL.md                   ← main skill: detect → interview → output flow
  helpers/
    detect.md                ← gap classification and detection interpretation
    universal-snippets.md    ← .claude/settings.json, init.sh, CI, CLAUDE.md template
    node-snippets.md         ← Node/TS paste-ready configs
    python-snippets.md       ← Python paste-ready configs
```

The root `SKILL.md` is intentionally left empty for user-managed content.

## Installation

Add this repository as a plugin in your Claude Code settings:

```json
{
  "plugins": [
    { "type": "git", "url": "https://github.com/your-org/harness-skill" }
  ]
}
```

## Evals

Acceptance criteria are defined in `evals/evals.json`. Four eval prompts cover:

1. Session-start checklist for a multi-hour task
2. Goal structure for a week-long autonomous task
3. CLAUDE.md quality guidance
4. Detection-first flow: identify gaps from a described project state

When modifying any skill file, verify the updated skill would still pass all four evals before committing.

## Reference

`2026-05-18-m1-engineering-standards.md` is the canonical "full harness" example for a Next.js + TypeScript project — the reference for what the skill should recommend at maximum depth.
