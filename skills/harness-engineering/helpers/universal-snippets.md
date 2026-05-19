# Universal Snippets

Paste-ready configs that apply regardless of stack. Inline comments mark what
to customise; everything else is a working default.

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
            "prompt": "Before ending this turn: have you run the project build and lint? If this was UI work, have you opened the feature in a browser? If any check is outstanding, complete it now."
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

## Global Constraints

Apply these to every implementation decision:

- **KISS** — prefer the simplest solution. If a simpler path exists, say so before implementing.
- **YAGNI** — no features, abstractions, or flexibility beyond what was asked.
- **DRY** — shared logic belongs in one place. Flag duplication before introducing it.
- **First Principles** — before adding any layer (abstraction, wrapper, helper), name the specific problem it solves. No clear problem = don't add it.
- **Occam's Razor** — when multiple approaches work, prefer the fewest components and dependencies.

## Stack

<!-- e.g. Next.js 14 · TypeScript · Prisma · Supabase · Tailwind -->
[FILL IN]

## Key Commands

```bash
# Start dev server
[FILL IN]

# Build
[FILL IN]

# Lint
[FILL IN]

# Type check
[FILL IN]

# Run tests
[FILL IN]
```

## Architecture

<!-- 2-3 sentences on the key boundaries that matter. Not a file tree. -->
[FILL IN]

## Gotchas

<!-- Real non-obvious traps that would bite a developer new to this codebase. -->
<!-- If none yet, delete this section. -->

## Skills

<!-- Trigger reminders — delete any that don't apply -->
- New feature or component: `brainstorming` skill first
- Any implementation task: `writing-plans` skill
- Claiming work complete: `verification-before-completion` skill
- Debugging failures: `systematic-debugging` skill

<important if="you are writing or modifying tests">
- Run the full test suite before marking any task done
- Use the project's existing test helpers and fixtures — don't invent new patterns
</important>

<important if="you are editing a route handler or API endpoint">
- Auth check must be the first operation
- Return `{ data: T }` on success, `{ error: string }` on failure — no bare responses
</important>
```

---

After writing, verify all five principles appear:
```bash
grep -c "KISS\|YAGNI\|DRY\|First Principles\|Occam" skills/harness-engineering/helpers/universal-snippets.md
```
Expected: 5 or more matches.

Then commit:
```bash
git add skills/harness-engineering/helpers/universal-snippets.md
git commit -m "feat(skill): add universal-snippets.md with hooks, init.sh, CI, and CLAUDE.md template"
```
