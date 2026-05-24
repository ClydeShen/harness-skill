# Kiro Snippets

Paste-ready configs for Kiro runtime. Kiro hooks live in `.kiro/hooks/` as JSON
files; steering files live in `.kiro/steering/` as Markdown.

> **Format note:** Kiro's hook JSON schema evolves with each release. Verify
> field names against your installed version's docs (`kiro docs hooks`) before
> committing. The trigger types and action types below are stable as of mid-2025.

## Contents
- [Hooks: .kiro/hooks/](#kirohooks--post-tool-use--stop-equivalents)
- [Steering: .kiro/steering/project.md](#kirosteeringprojectmd--instruction-file)

---

## .kiro/hooks/ — Post-Tool-Use + Stop equivalents

Kiro's "Post Tool Use" trigger covers the same failure mode as Claude Code's
`PostToolUse` hook (silent lint drift). "Agent Turn Completion" covers the same
failure mode as the `Stop` hook (premature done declarations).

Create two files:

### .kiro/hooks/post-tool-lint.json

```json
{
  "name": "post-tool-lint",
  "description": "Run linter after every file edit to catch violations immediately",
  "trigger": {
    "type": "postToolUse",
    "tools": ["editFile", "writeFile"]
  },
  "action": {
    "type": "command",
    "command": "npx eslint --fix \"${file}\""
  },
  "enabled": true
}
```

Note: Replace `npx eslint --fix` with your stack's linter:
- Python: `ruff check --fix "${file}"`
- Go: `gofmt -w "${file}"`

### .kiro/hooks/agent-stop-verify.json

```json
{
  "name": "agent-stop-verify",
  "description": "Force verification before agent declares done",
  "trigger": {
    "type": "agentTurnEnd"
  },
  "action": {
    "type": "prompt",
    "prompt": "Before ending this turn: (1) Run the project build and lint — fix any errors now, not later. (2) If this was UI work, open the feature in a browser and confirm the behavior is observable end-to-end. (3) Write a two-sentence status summary: what was changed and what the next concrete step is. Complete all outstanding checks before finishing."
  },
  "enabled": true
}
```

---

## .kiro/steering/project.md — Instruction file

Kiro's equivalent of `CLAUDE.md`. Lives at `.kiro/steering/project.md`.
The `inclusion: always` front matter loads it on every agent turn.

60-line target. Hard ceiling: 200 lines.

```markdown
---
inclusion: always
---

# Project Standards

## 1. Think Before Coding

Don't assume. Surface tradeoffs before writing code.

- New feature / "build X": explore intent and tradeoffs before writing any code
- Bug / error / test failure: identify root cause before proposing a fix
- Multi-step task (3+ files or >1 hr): write a step-by-step plan before touching files

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked. No abstractions for single-use code.
- After writing code, before commit: review for dead code and overcomplication

## 3. Surgical Changes

Touch only what you must. Match existing style.

- Every changed line must trace to the request — no adjacent "improvements"
- Destructive command (`rm -rf`, force-push, DROP TABLE): warn and confirm before running

## 4. Goal-Driven Execution

Define success criteria. Loop until verified.

- Transform tasks into verifiable goals: "Fix X" → "write a test that reproduces it, then make it pass"
- For multi-step tasks, write a brief plan — each step has a concrete verify check

## Stack

<!-- e.g. Next.js 14 · TypeScript · Supabase · Stripe -->
[FILL IN]

## Key Commands

```bash
# Start dev server  [FILL IN]
# Build             [FILL IN]
# Lint              [FILL IN]
# Run tests         [FILL IN]
```

## Architecture

<!-- 2-3 sentences on key boundaries. Not a file tree. -->
[FILL IN]

## Gotchas

<!-- Non-obvious traps only. Delete if none. -->
```

If the steering file grows past 100 lines, use Kiro's conditional inclusion:

```markdown
---
inclusion: fileMatch
fileMatchPattern: "src/api/**"
---

- Auth check must be the first operation
- Return `{ data: T }` on success, `{ error: string }` on failure
```
