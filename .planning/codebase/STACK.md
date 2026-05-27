# Stack
_Generated: 2026-05-27_

## Languages & Runtimes

- **Python 3.11** — eval runner (`evals/run_evals.py`), promptfoo providers (`evals/promptfoo/provider.py`, `grader.py`, `scaffold_helper.py`, `provider_pi.py`)
- **JavaScript / Node.js 22** (detected at runtime; CI pins Node 20) — promptfoo CLI execution via `npm run eval:*` scripts
- **Bash** — install and utility scripts (`scripts/link-skills.sh`, `scripts/list-skills.sh`, `init.sh`, `.claude-plugin/link-skills.sh`), GitHub Actions workflow steps
- **YAML** — promptfoo eval configs (`evals/promptfoo/*.yaml`), pre-commit config (`.pre-commit-config.yaml`), GitHub Actions workflows (`.github/workflows/*.yml`)
- **Markdown** — all skill definitions (`skills/**/SKILL.md`, `skills/**/references/*.md`), documentation

## Package Managers

- **npm 11** with lockfile v3 (`package-lock.json` present and committed)
  - Lockfile: present (`package-lock.json`)
- **pip / Python standard library** — no `requirements.txt` or `pyproject.toml`; Python deps (`requests`) must be installed separately
- **pre-commit** — hook manager configured via `.pre-commit-config.yaml`

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `promptfoo` | `0.120.19` | Eval runner — executes YAML-defined test suites against skill responses |
| `requests` (Python) | stdlib/external | HTTP client used by `provider.py` and `grader.py` to call the llamacpp server at `localhost:8080` |

> No runtime application dependencies exist. The repo is a content/tooling project; `node_modules` contains only `promptfoo` and its transitive deps.

## Build / Tooling

**Eval runner:**
```bash
python evals/run_evals.py                          # all skills
python evals/run_evals.py --skill harness-audit    # one skill
python evals/run_evals.py --skill triage --filter "#2"  # filtered
```

**npm scripts** (defined in `package.json`):
```bash
npm run eval           # promptfoo eval --no-cache --no-share
npm run eval:view      # promptfoo view  (open results UI)
npm run eval:one       # run first eval case only
npm run eval:validate  # validate promptfoo config syntax
```

**Pre-commit hooks** (`.pre-commit-config.yaml`, rev `v4.6.0`):
- `trailing-whitespace`
- `end-of-file-fixer`
- `check-yaml`
- `check-json`
- `check-merge-conflict`
- `mixed-line-ending` (enforces LF)

**Claude Code hooks** (`.claude/settings.json`):
- `Stop` hook: reminds to run `eval:validate` and check git diff before declaring done
- `PostToolUse` (Write): reminds to run `python evals/run_evals.py --skill <name>` after editing any `SKILL.md`

**No linter or formatter** is configured for Python or Markdown beyond pre-commit checks.

## Dev Environment

**Required local services:**
- `llamacpp` HTTP server running at `localhost:8080` — both the response model and LLM judge connect to this endpoint
  - Response model: `qwen2.5-coder-32b-instruct-q5_k_m.gguf` (set in `evals/promptfoo/provider.py`)
  - Judge model: `Qwen3.6-35B-A3B-UD-Q5_K_M.gguf` (set in `evals/promptfoo/grader.py`)
  - Alternative: `llamacpp/qwen3.6-35b-a3b-ud-q5_k_m` via `pi` CLI (`provider_pi.py`)

**Setup:**
```bash
bash init.sh   # installs npm deps, validates promptfoo config, checks Python syntax
```

**Skill installation** (links skills into Claude's skills directory):
```bash
bash scripts/link-skills.sh   # symlinks skills/*/* → ~/.claude/skills/
```

**No Docker, no `.env` file, no environment variables required** for normal operation. The llamacpp server URL is hardcoded in `evals/promptfoo/provider.py` and `grader.py`.
