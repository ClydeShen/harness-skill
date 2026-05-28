# Integrations
_Generated: 2026-05-27_

## External Services

**llamacpp HTTP server (localhost:8080)**
- Role: LLM inference backend for both response generation and LLM-judge grading
- Used by: `evals/promptfoo/provider.py` (response), `evals/promptfoo/grader.py` (judge)
- Endpoint: `http://localhost:8080/v1/chat/completions` (OpenAI-compatible)
- Not a hosted SaaS — must be run locally before executing evals
- Response model: `qwen2.5-coder-32b-instruct-q5_k_m.gguf`
- Judge model: `Qwen3.6-35B-A3B-UD-Q5_K_M.gguf`

**pi CLI (reference only)**
- Role: Alternative provider invoking skills via the `pi` CLI binary
- Used by: `evals/promptfoo/provider_pi.py` (reference implementation, not used in CI)
- Model alias: `llamacpp/qwen3.6-35b-a3b-ud-q5_k_m`

## MCP Servers

No MCP server configuration detected in this repository. The `.pi/settings.json` file exists but contains only `{}`.

## CI/CD

**GitHub Actions** — `.github/workflows/`

### `ci.yml` — Validation pipeline
- Triggers: push to `main`, pull requests targeting `main`
- Runner: `ubuntu-latest`
- Steps:
  1. `actions/checkout@v4`
  2. `actions/setup-node@v4` with Node 20, npm cache
  3. `npm ci` — install dependencies
  4. `npm run eval:validate` — validate promptfoo config syntax
  5. `actions/setup-python@v5` with Python 3.11
  6. `python -m py_compile` — syntax check all eval Python files
- Does NOT run full evals (requires local llamacpp server)

### `sync-status.yml` — GitHub Project board automation
- Triggers: issue labeled, PR opened/closed/reopened, `workflow_dispatch` (manual backfill)
- Runner: `ubuntu-latest`
- Purpose: Keeps GitHub Projects v2 board columns in sync with `status:*` issue labels
- Project ID: `PVT_kwHOAPZRDM4BYnKy`
- Status field ID: `PVTSSF_lAHOAPZRDM4BYnKyzhTrw68`
- Target repo: `ClydeShen/harness-skill`
- Secret used: `GH_PROJECT_TOKEN` (falls back to `github.token`)
- Three jobs:
  - `sync-label`: maps `status:*` labels to board column option IDs
  - `sync-pr`: on PR open/close/merge, updates linked issue labels and board columns
  - `backfill`: manual dispatch to bulk-sync all open issues with status labels to board

**Status label → board column mapping:**
| Label | Option ID |
|-------|-----------|
| `status:needs-triage`, `status:needs-info` | `f75ad846` |
| `status:needs-prd` | `61e4505c` |
| `status:needs-review` | `47fc9ee4` |
| `status:ready-for-agent`, `status:ready-for-human` | `df73e18b` |
| `status:in-progress` | `8981fc42` |
| `status:done`, `status:wontfix` | `98236657` |

## Plugin / Extension System

**Claude Code plugin** (`.claude-plugin/`)
- `plugin.json` — declares plugin name (`harness-audit-skills` v2.4.0) and lists 15 skill paths
- `link-skills.sh` — symlinks all `skills/*/<name>/` directories into `~/.claude/skills/`
- Skills are loaded by Claude Code via the `/skill-name` invocation pattern

**Registered skills in `plugin.json`:**
- Engineering (10): `harness-audit`, `setup-harness-skills`, `context-handover`, `session-start`, `triage`, `to-prd`, `to-issues`, `zoom-out`, `grill-with-docs`, `harness-guide`
- Productivity (5): `caveman`, `grill-me`, `handoff`, `write-a-skill`, `skill-cleanup`

**promptfoo eval plugin** (`evals/promptfoo/`)
- Each skill has a dedicated YAML config (`<skill-name>.yaml`) consumed by the `run_evals.py` runner
- Custom Python providers (`provider.py`, `grader.py`) integrate with the llamacpp inference backend
- Per-skill configs present: `context-handover.yaml`, `harness-audit.yaml`, `harness-guide.yaml`, `session-start.yaml`, `setup-harness-skills.yaml`

**pre-commit hooks** (`.pre-commit-config.yaml`)
- Source: `https://github.com/pre-commit/pre-commit-hooks` rev `v4.6.0`
- Enforces file hygiene (whitespace, EOF, YAML/JSON validity, merge conflict markers, LF line endings)
