# Conventions
_Generated: 2026-05-27_

## Code Style

### Python (eval infrastructure)
- Python 3.11+ syntax; uses `str | None` union syntax (PEP 604), not `Optional[str]`
- Type hints on all function signatures in `evals/promptfoo/`
- `list[Path]`, `dict[str, str]` lowercase generics (PEP 585), not `List`, `Dict`
- Module-level constants in ALL_CAPS: `PROMPTFOO_DIR`, `API_BASE`, `MODEL`, `REPO_ROOT`
- `_private_helpers` prefixed with underscore for module-internal functions
- `textwrap.dedent()` for all multi-line string literals in `evals/promptfoo/scaffold_helper.py`
- `from pathlib import Path` — use `Path` objects throughout, never string concatenation for paths
- No f-strings for SQL/JSON — use `json.dumps()` and `json.loads()` explicitly

### Markdown / Skill content
- Skill prose is plain Markdown; no HTML tags except `<important if>` tags in CLAUDE.md templates
- Bold (`**text**`) for emphasis on terms, gap names, and invariants
- Inline code (`` `path/to/file` ``) for every file path, command, and config key
- Code blocks with language tag: ` ```json `, ` ```bash `, ` ```yaml `, ` ```markdown `
- Section headers use `##` and `###` — no `####` or deeper

### JSON (skill.json, evals.json, plugin.json)
- 2-space indentation, no trailing commas
- `skill.json` keys in order: `name`, `version`, `description`, `author`, `verticals`, `tags`, `scripts`
- `evals.json` uses `"id"` (integer), `"prompt"`, `"expected_output"`, `"files"`, `"expectations"` keys

---

## Formatting / Linting

### Python syntax gate (CI)
```bash
python -m py_compile evals/run_evals.py evals/promptfoo/provider.py \
  evals/promptfoo/grader.py evals/promptfoo/scaffold_helper.py
```
Run by `.github/workflows/ci.yml`. No autoformatter (black/ruff) is configured — keep style consistent with existing files manually.

### promptfoo YAML validation (CI)
```bash
npm run eval:validate
# expands to: promptfoo validate config -c evals/promptfoo/promptfooconfig.yaml
```
Validates all YAML configs against the promptfoo JSON schema. Run locally before committing any `.yaml` changes.

### No JS/TS linting
The repo has no ESLint or Prettier config. `package.json` contains only `promptfoo` as a dev dependency and eval scripts.

---

## Git Conventions

### Commit message format
```
<type>(<scope>): <short description>

# Types observed in this repo:
feat       — new skill or eval scenario
fix        — correction to skill logic, snippet, or invariant
chore      — session close, dependency update, housekeeping
refactor   — restructuring without behavior change
```

- Scope is the skill name or area: `(harness-audit)`, `(evals)`, `(#4)` (issue number)
- Short description is imperative, lowercase, no period
- Issue numbers appear as `(#N)` in scope or `— #N` suffix: `feat(#4): add harness-guide skill`
- Session-close commits use: `chore: close session — #N complete, all issues resolved`

### Branch naming
- Feature branches: `feat/<skill-name>` or `feat/issue-<N>`
- Fix branches: `fix/<description>`
- Work from `main` directly for small changes; PRs for multi-commit work

### Pre-commit gate
No `.pre-commit-config.yaml` or `.husky/` in this repo. The CI pipeline serves as the merge gate.

---

## Skill Authoring Conventions

### Required files per skill
```
skills/<bucket>/<skill-name>/
  SKILL.md          ← skill logic + system prompt (required)
  skill.json        ← metadata (required for harness-audit and harness-guide only)
  evals/
    evals.json      ← legacy acceptance criteria (required for all skills)
  references/       ← optional; stack-specific and reference content
    universal-snippets.md
    node-snippets.md
    python-snippets.md
    <topic>.md
```

### SKILL.md structure
Every `SKILL.md` opens with a YAML frontmatter block:
```yaml
---
name: <skill-name>
description: |
  <one-paragraph description used by npx skills discovery>
  Include trigger phrases at the end of the description line.
---
```
The frontmatter is stripped by `provider.py` before injecting as system prompt.

After frontmatter:
1. Role declaration (bold, one sentence): `**You are a [role]. Never [anti-pattern].**`
2. Phase sections (`## Phase 1 — Detect`, `## Phase 2 — Interview`, `## Phase 3 — Output`) or equivalent
3. Behavioral rules that apply throughout
4. Output format template (exact section headers, field names)

### Every gate must justify itself
Every detection check or gate recommendation in `SKILL.md` must include a failure-mode sentence:
```
`.claude/settings.json` absent → **Gap: Missing Stop hook.**
Why it matters: Without it, Claude declares tasks complete without verifying.
```
No failure mode = do not add the gate (YAGNI).

### Snippet rules
- Snippets in `references/` are not duplicated — stack-specific content goes in `node-snippets.md` or `python-snippets.md`, not in `universal-snippets.md`
- Every snippet must be paste-ready with no `YOUR_PROJECT_NAME` placeholders
- Inline comments (`# --- Customise ---`) mark what to change; everything else is a working default
- Hook JSON uses `"matcher": ""` (plain string), `"type": "command"` — not `"type": "prompt"` or object matchers

### skill.json
Only `harness-audit` and `harness-guide` have `skill.json`. New skills that need package metadata follow:
```json
{
  "name": "<skill-name>",
  "version": "0.1.0",
  "description": "<one line>",
  "author": { "name": "Clyde Shen", "github": "ClydeShen" },
  "verticals": ["productivity"],
  "tags": ["claude", "<relevant-tags>"],
  "scripts": { "setup": "" }
}
```

### Bucket and registry
Every new skill requires:
1. Entry in `skills/<bucket>/README.md` with one-line description and link to `SKILL.md`
2. Entry in top-level `README.md` reference table
3. Entry in `.claude-plugin/plugin.json` `"skills"` array

### Eval authoring
Add new scenarios to `evals/promptfoo/<skill>.yaml` first, then update `SKILL.md` to cover it.
Each eval test has:
- `description`: `"#N <short label>"` (number + label for `--filter` targeting)
- `vars.prompt`: realistic user message
- `vars.scaffold_files`: list of plain-English file hints for `scaffold_helper.py`
- `assert`: mix of `llm-rubric` (semantic) and `icontains`/`not-icontains` (literal) assertions

---

## Documentation Conventions

### README.md files
- Top-level `README.md`: quickstart + reference table for all skills (name → SKILL.md link)
- `skills/engineering/README.md` and `skills/productivity/README.md`: one-line descriptions only
- No deep documentation in README — deep content lives in `SKILL.md` and `references/*.md`

### Inline documentation
- Python files: module-level docstring explaining purpose and key config (see `provider.py`, `grader.py`)
- No per-function docstrings unless behavior is non-obvious
- YAML eval files: comment block before each test using the separator pattern:
  ```yaml
  # ---------------------------------------------------------------------------
  # Eval N: <short description>
  # ---------------------------------------------------------------------------
  ```

### Reference files
- `universal-snippets.md`: stack-agnostic snippets with a TOC at the top
- `node-snippets.md` / `python-snippets.md`: stack-specific overrides
- `scenarios.md`: edge-case scenario descriptions (not snippets)
- `detect.md`: detection logic reference
- No duplication between reference files
