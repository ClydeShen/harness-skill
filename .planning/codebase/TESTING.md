# Testing
_Generated: 2026-05-27_

## Test Strategy

This repo has no unit tests for application code. The only testable artifacts are the skill prompts (`SKILL.md` + `references/*.md`). The test suite is an **LLM eval suite** that sends realistic prompts to a local model and judges the responses against semantic rubrics.

Philosophy:
- Evals test _behavioral invariants_, not string outputs — every assertion is a rubric question answered by an LLM judge
- Each eval scenario maps to one documented invariant in `SKILL.md` (or a regression from a found bug)
- Adding a scenario to `evals/promptfoo/<skill>.yaml` always precedes updating `SKILL.md` to cover it
- Before committing any skill file change, run the skill's evals and confirm all pass

---

## Test Types

### LLM evals (primary — via promptfoo)
Located in `evals/promptfoo/<skill-name>.yaml`. Currently 5 skills have promptfoo eval configs:
- `evals/promptfoo/harness-audit.yaml` — 16 scenarios covering all detection checks and invariants
- `evals/promptfoo/harness-guide.yaml` — 5 scenarios covering bucket classification and coaching loop
- `evals/promptfoo/setup-harness-skills.yaml` — 4 scenarios covering explore-first and update behavior
- `evals/promptfoo/context-handover.yaml` — 3 scenarios covering handoff doc format and fallback
- `evals/promptfoo/session-start.yaml` — 4 scenarios covering briefing format and recovery

### Legacy acceptance criteria (evals.json)
Located at `skills/<bucket>/<skill>/evals/evals.json`. Present for all 13 skills (including those without promptfoo configs). Format is human-readable JSON with `"expectations"` arrays. These are reference documentation for expected behavior, not executed tests. The promptfoo `.yaml` configs are the canonical executed tests.

### Python syntax check (CI)
Not a test framework — `python -m py_compile` checks eval infrastructure files for syntax errors. Runs in CI on every push/PR.

### promptfoo config validation (CI)
`npm run eval:validate` runs `promptfoo validate config` against the YAML schema. Catches malformed assertion types and missing required fields before running actual evals.

---

## Eval Framework

### Architecture

```
evals/
  run_evals.py             ← CLI runner: discovers configs, invokes promptfoo per skill
  promptfoo/
    <skill>.yaml           ← eval config: prompts, provider, assertions
    provider.py            ← response provider: builds system prompt, scaffolds project, calls llamacpp
    grader.py              ← judge provider: LLM-based pass/fail verdict
    scaffold_helper.py     ← creates realistic temp project dirs from plain-English hints
    provider_pi.py         ← reference-only Pi CLI provider (not used in CI)
```

### How an eval run works

1. `run_evals.py` discovers `evals/promptfoo/*.yaml` configs
2. For each config, invokes `promptfoo eval --config <skill>.yaml --no-cache`
3. promptfoo calls `provider.py` for each test case:
   - Loads `SKILL.md` + all `references/*.md` as the system prompt (cached per skill)
   - Strips YAML frontmatter from `SKILL.md` before injection
   - Creates a temporary project directory via `scaffold_helper.scaffold()`
   - Builds a file listing of that temp dir and prepends it to the user message
   - Sends `{system, user}` to llamacpp HTTP at `localhost:8080`
4. promptfoo calls `grader.py` for each assertion:
   - `llm-rubric` assertions: sends full grading prompt to llamacpp judge model
   - `icontains`/`not-icontains` assertions: handled natively by promptfoo (no LLM call)
   - Judge returns `{"pass": bool, "score": float, "reason": "one sentence"}`

### Model configuration

Response model (set in `evals/promptfoo/provider.py`):
```python
API_BASE = "http://localhost:8080/v1"
MODEL = "qwen2.5-coder-32b-instruct-q5_k_m.gguf"
```

Judge model (set in `evals/promptfoo/grader.py`):
```python
API_BASE = "http://localhost:8080/v1"
MODEL = "Qwen3.6-35B-A3B-UD-Q5_K_M.gguf"
```
Both use the same llamacpp server. Temperature 0.1 for response, 0 for judge.

### Assertion types used

| Type | Evaluated by | Use case |
|------|-------------|----------|
| `llm-rubric` | `grader.py` (LLM judge) | Semantic behavioral checks |
| `icontains` | promptfoo native | Must contain exact string (e.g., `"Kiro"`, `"GEMINI.md"`) |
| `not-icontains` | promptfoo native | Must NOT contain exact string |
| `latency` | promptfoo native | Timeout guard — 300 000 ms (5 min) per test |

### Scaffold system

`scaffold_helper.scaffold(tmpdir, scaffold_files)` interprets plain-English entries from `vars.scaffold_files`:

```yaml
scaffold_files:
  - "package.json with next.js and typescript"
  - ".claude/settings.json with Stop and PostToolUse hooks"
  - "CLAUDE.md at 90 lines"
  - "no .github/workflows/"
```

The helper matches substrings case-insensitively to create real files in a temp dir. Supported hints include: `package.json`, `tsconfig.json`, `.github/workflows/ci.yml` (with or without lint), `CLAUDE.md` (250-line, 90-line, or basic), `AGENTS.md`, `.claude/settings.json` (full hooks or PostToolUse-only), `.planning/STATE.md` (idle or interrupted), `.planning/config.json` (with or without harness key), `docs/agents/` (five seed files), `.kiro/`, `.gemini/`, `requirements.txt`, `MEMORY.md`, `.git/config`.

---

## Running Tests

### Prerequisites
- `promptfoo` on PATH (installed via `npm ci` from `package.json`)
- llamacpp server running at `localhost:8080` with both models loaded
- Python 3.11+

### Commands

```bash
# Run all skills with evals:
python evals/run_evals.py

# Run one skill:
python evals/run_evals.py --skill harness-audit

# Run a single scenario (regex matched against description):
python evals/run_evals.py --skill harness-audit --filter "#4"

# Run promptfoo directly for a skill (from evals/promptfoo/ directory):
cd evals/promptfoo && promptfoo eval --config harness-audit.yaml

# Validate YAML configs only (no LLM calls — runs in CI):
npm run eval:validate

# Check Python syntax only (no LLM calls — runs in CI):
python -m py_compile evals/run_evals.py evals/promptfoo/provider.py \
  evals/promptfoo/grader.py evals/promptfoo/scaffold_helper.py
```

### Output files
Each skill run writes `evals/promptfoo/output-<skill-name>.json`. These are gitignored implicitly (not committed).

---

## Coverage

### Skills with full promptfoo eval coverage (executed tests)
| Skill | Scenarios | Key invariants tested |
|-------|-----------|----------------------|
| `harness-audit` | 16 | Stop hook priority, AGENTS.md equivalence, brownfield, Kiro/Gemini runtimes, hook snippet schema, partial hooks, memory gap ranking |
| `harness-guide` | 5 | Three-bucket classification, inspect-first, single next-step enforcement, anti-pattern detection |
| `setup-harness-skills` | 4 | Explore-first, update vs. overwrite, instruction file choice, GSD config merge |
| `context-handover` | 3 | `.continue-here.md` format, STATE.md update, fallback on missing state |
| `session-start` | 4 | Briefing before action, recovery vs. normal session, reads-before-questions, interrupted session |

### Skills with legacy evals.json only (not executed automatically)
`triage`, `to-prd`, `to-issues`, `zoom-out`, `grill-with-docs`, `caveman`, `grill-me`, `handoff`, `write-a-skill`

### Coverage gaps
- 9 of 14 skills have no promptfoo eval configs — behavioral regressions in these skills are undetected by CI
- No eval covers multi-turn / follow-up behavior (all evals are single-turn)
- No eval covers the `recommended-skills` section rendering when both GSD Redux and Superpowers are absent simultaneously (eval #15 covers GSD Redux only)
- `harness-guide` coaching loop (re-run after user acts) is not tested — only the initial classification pass
- `session-start` eval #4 (interrupted session recovery) requires `.continue-here.md` scaffold; the git log delta assertion cannot be verified without an actual git repo in the temp dir
