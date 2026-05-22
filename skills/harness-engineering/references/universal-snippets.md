# Universal Snippets

Paste-ready configs that apply regardless of stack. Inline comments mark what
to customise; everything else is a working default.

## Contents
- [Hooks: .claude/settings.json](#claudes-settingsjson--hooks)
- [Health check: init.sh](#initsh--environment-health-check)
- [CI pipeline: .github/workflows/ci.yml](#githubworkflowsciyml--ci-pipeline)
- [Project template: CLAUDE.md](#claudemd--project-template)

---

## .claude/settings.json — Hooks

Closes the two most common failure modes: silent lint drift and premature
done declarations.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix \"$CLAUDE_FILE_PATH\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before ending this turn: (1) Run the project build and lint — fix any errors now, not later. (2) If this was UI work, open the feature in a browser and confirm the behavior is observable end-to-end. (3) Write a two-sentence status summary: what was changed and what the next concrete step is. Complete all outstanding checks before finishing."
          }
        ]
      }
    ]
  }
}
```

Note: Replace the `npx eslint --fix` command with your stack's linter:
- Python: `ruff check --fix "$CLAUDE_FILE_PATH"`
- Go: `gofmt -w "$CLAUDE_FILE_PATH"`

---

## init.sh — Environment Health Check

Place at project root. Run at the start of every session.
Exits non-zero if any check fails — do not start work if this fails.

```bash
#!/usr/bin/env bash
set -e

echo "=== Environment Health Check ==="

# --- Customise the checks below for your stack ---

# Node.js version check (remove if not a Node project)
if command -v node &>/dev/null; then
  node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
  [ "$node_version" -ge 20 ] || { echo "ERROR: Node.js >= 20 required"; exit 1; }
  echo "✓ Node.js $(node -v)"
fi

# Python version check (remove if not a Python project)
if command -v python3 &>/dev/null; then
  py_version=$(python3 -c "import sys; print(sys.version_info.minor)")
  [ "$py_version" -ge 11 ] || { echo "ERROR: Python >= 3.11 required"; exit 1; }
  echo "✓ Python $(python3 --version)"
fi

# .env.local or .env must exist
[ -f ".env.local" ] || [ -f ".env" ] || {
  echo "ERROR: .env.local or .env missing — copy from .env.example"
  exit 1
}
echo "✓ env file present"

# TypeScript clean (Node/TS projects)
if [ -f "tsconfig.json" ]; then
  npx tsc --noEmit && echo "✓ TypeScript clean" || {
    echo "ERROR: TypeScript errors present"
    exit 1
  }
fi

# Python type check (Python projects)
if [ -f "pyproject.toml" ] && command -v mypy &>/dev/null; then
  mypy . --ignore-missing-imports && echo "✓ mypy clean" || {
    echo "ERROR: mypy errors present"
    exit 1
  }
fi

echo "=== Ready ==="
```

Make it executable after creating it:

```bash
chmod +x init.sh
```

---

## .github/workflows/ci.yml — CI Pipeline

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Node/TS — remove if not applicable
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run build

      # Python — uncomment if applicable
      # - uses: actions/setup-python@v5
      #   with:
      #     python-version: '3.11'
      # - run: pip install uv && uv sync
      # - run: ruff check .
      # - run: mypy .
```

---

## CLAUDE.md — Project Template

60-line target. Fill in the bracketed sections; delete sections that don't apply.

```markdown
# CLAUDE.md

## 1. Think Before Coding

Don't assume. Surface tradeoffs before writing code.

- New feature / "build X": explore intent and tradeoffs before writing any code
- Bug / error / test failure: identify root cause before proposing a fix
- Multi-step task (3+ files or >1 hr): write a step-by-step plan before touching files

## 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked. No abstractions for single-use code.
- No error handling for impossible scenarios. If 200 lines could be 50, rewrite it.
- After writing code, before commit: review for dead code and overcomplication
- Dead code / unused imports: remove dead code and unused imports
- AI-generated or vibe-coded code: audit AI-generated code for quality
- Code quality check: check typecheck, lint, test, and dead code coverage

## 3. Surgical Changes

Touch only what you must. Match existing style.

- Every changed line must trace to the request — no adjacent "improvements"
- Scope-creep risk: limit edits to the affected directory until the fix is confirmed
- Destructive command (`rm -rf`, force-push, DROP TABLE): warn and confirm before running
- Need checkout isolation: use git worktrees
- Frontend issue detector: detect and debug frontend issues in a real browser

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

- Transform tasks into verifiable goals: "Fix X" → "write a test that reproduces it, then make it pass"
- For multi-step tasks, write a brief plan — each step has a concrete verify check
- Weak criteria ("make it work") require constant clarification — define done before starting

## Stack

<!-- e.g. Next.js 14 · TypeScript · Prisma · Supabase · Tailwind -->
[FILL IN]

## Key Commands

```bash
# Start dev server  [FILL IN]
# Build             [FILL IN]
# Lint              [FILL IN]
# Type check        [FILL IN]
# Run tests         [FILL IN]
```

## Architecture

<!-- 2-3 sentences on key boundaries. Not a file tree. -->
[FILL IN]

## Gotchas

<!-- Non-obvious traps only. Delete if none. -->

## Skills

<!-- gsd-2 (priority when installed): `/gsd` or `/gsd auto` (milestones/autonomous), `/gsd discuss` (feature/architecture), `/gsd quick` (quick tasks)

Think before coding:
- New feature / "build X":    `brainstorming` skill
- Bug / error / failure:      `systematic-debugging` skill
- Multi-step / 3+ files:      `writing-plans` skill

Simplicity first:
- After writing code:         `simplify` skill
- Dead code / unused imports: `refactor-cleaner` skill
- AI-generated cleanup:       `vibe-code-auditor` skill
- Code quality dashboard:     `health` skill

Surgical changes:
- Scope-creep risk:           `freeze` skill
- Destructive ops:            `careful` / `guard` skill
- Worktree isolation:         `using-git-worktrees` skill
- Frontend issue detector:    `vercel-labs/agent-browser` skill (frontend only)
-->

<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use existing test helpers — don't invent new patterns
</important>

<important if="you are editing a route handler or API endpoint">
- Auth check must be the first operation
- Return `{ data: T }` on success, `{ error: string }` on failure
</important>
```

**Target: 60 lines. Hard ceiling: 200 lines per file.**

If CLAUDE.md grows past 100 lines, move path-specific rules to `.claude/rules/`:

```
.claude/rules/
  testing.md      # rules that apply only when editing test files
  api.md          # rules that apply only to route handlers
```

Each rules file can carry path frontmatter so it loads only when matching files are opened:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

- Auth check must be the first operation
- Return `{ data: T }` on success, `{ error: string }` on failure
```

---

## Gemini Adaptation Notes

When the detected runtime is Gemini, output the universal CI and init.sh snippets
unchanged. For Claude-specific items, substitute as follows:

| Claude Code item | Gemini equivalent |
|---|---|
| `.claude/settings.json` hooks | No documented equivalent — note: "Verify hook support in your Gemini agent's settings" |
| `CLAUDE.md` | `GEMINI.md` — same template structure, same 200-line ceiling |
| `.claude/rules/` | No equivalent — consolidate all rules into `GEMINI.md` with clear section headers |
| `<important if="...">` tags | No equivalent — use `GEMINI.md` section headers to group task-specific rules |

Always tell the user which items are Gemini-adapted vs. universal so they understand what to verify.
