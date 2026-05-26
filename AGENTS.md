# AGENTS.md

## Repo Overview

`harness-engineering-skill` — a curated skill collection for compound engineering workflows,
packaged as a Claude Code / Codex plugin.

All 13 skills are implemented across `skills/engineering/` and `skills/productivity/`.
See `skills/engineering/README.md` and `skills/productivity/README.md` for the full list.

Install via `bash scripts/link-skills.sh`. Skills live under `skills/engineering/` or `skills/productivity/`.

## Skill Structure

```
skills/
  engineering/
    harness-audit/      ← detect harness gaps, output snippets
      SKILL.md
      skill.json
      evals/evals.json
      references/
    setup-harness-skills/  context-handover/  session-start/
    triage/  to-prd/  to-issues/  zoom-out/  grill-with-docs/
  productivity/
    caveman/  grill-me/  handoff/  write-a-skill/
evals/
  run_evals.py               ← discovers and runs all skill evals
.claude-plugin/
  plugin.json                ← registered skill list
  link-skills.sh             ← symlinks skills/ into ~/.claude/skills/
scripts/
  link-skills.sh
  list-skills.sh
```

## Build / Test

```bash
# All skills:
python evals/run_evals.py

# One skill only:
python evals/run_evals.py --skill harness-audit

# Filter to specific evals (regex matched against description):
python evals/run_evals.py --skill harness-audit --filter "#2"
```

Requires `promptfoo` on PATH and a llamacpp server running at `localhost:8080`.
Both the response provider and the LLM judge use the server (see `evals/promptfoo/provider.py` / `grader.py`).

## Key Invariants

- Stop hook is always gap #1 when `.claude/settings.json` is missing
- AGENTS.md is fully equivalent to CLAUDE.md — never flag missing CLAUDE.md when AGENTS.md is present
- Brownfield codebase: never tell users to fix all lint errors manually; recommend `eslint --fix`
- Multi-day scope output MUST include "one active task at a time", verification anti-patterns, and Judge audit as exit criterion
- Every snippet must be complete and paste-ready — no `YOUR_PROJECT_NAME` placeholders
- Before committing any change to a skill file, run `python evals/run_evals.py --skill <name>` and confirm all evals pass
