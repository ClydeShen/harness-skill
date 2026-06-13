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
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Before ending this turn: (1) Run the project build and lint — fix any errors now, not later. (2) If this was UI work, open the feature in a browser and confirm the behavior is observable end-to-end. (3) Write a two-sentence status summary: what was changed and what the next concrete step is. Complete all outstanding checks before finishing.'"
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

Drop-in behavioral guidelines. Merge with project-specific instructions as needed.

```markdown
# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
    3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Harness Discipline

**Long-running work fails silently. Epistemic gaps compound into errors. Make both kinds of boundary explicit.**

- Don't fabricate. Every factual claim must trace to observed evidence, documentation, or established best practice. Confidence is not a source — if you cannot ground a claim, say so rather than presenting it as fact.
- Earn confidence from independent dimensions, don't feel it. For any critical autonomous judgment, count how many of four independent dimensions affirm it: (1) the user's stated judgment, (2) your own derived reasoning, (3) established referenceable logic, code, or algorithms, (4) findings researched via websearch or tools. The count sets the level — 4 → high (0.9–1.0), 3 → medium (0.6–0.9), 2 → low (0.3–0.6), 1 → none (0–0.3). State the level and which dimensions back it; below medium, surface the gap before acting.
- It's OK not to know. Say so explicitly instead of guessing. Proactively surface information gaps and ask what you need to proceed — don't fill them with plausible-sounding assumptions.
- While implementing a spec, maintain a running `.harness/implementation-notes.md` capturing: decisions made that weren't covered by the spec, things that had to change from the original plan, tradeoffs you made, and anything else the human should know.
- Exit criteria must be observable: a gate that passed, not a feeling that it's done. Name the anti-patterns: Fuzzy Done, Proxy Signal, Confidence Exit.
- State lives outside the agent. The source of truth is the issue tracker, the handoff document, the config file — not working memory.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, clarifying questions come before implementation rather than after mistakes, and long-running sessions hand off cleanly without lost context.
```

**Hard ceiling: 200 lines per file.** Add project-specific sections (Stack, Key Commands, Architecture, Gotchas) after the guidelines above.

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
