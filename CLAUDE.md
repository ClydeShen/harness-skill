# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo is a curated skill collection for compound engineering workflows, packaged as a Claude Code / Codex plugin.

All 13 skills implemented across `skills/engineering/` and `skills/productivity/`. See `skills/engineering/README.md` and `skills/productivity/README.md` for the full list and source attribution.

Install via `bash scripts/link-skills.sh`. Skills live in `skills/engineering/` or `skills/productivity/`.

## Bucket Conventions

Skills are organised into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools

Every skill in either bucket must have a reference entry in the top-level `README.md` (linking the skill name to its `SKILL.md`) and an entry in `.claude-plugin/plugin.json`.

Each bucket folder has a `README.md` listing every skill with a one-line description and a link to its `SKILL.md`.

The root `SKILL.md` is absent by design — `npx skills` discovers skills from the bucket subfolders.

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
  run_evals.py               ← promptfoo runner (discovers all skill configs)
  promptfoo/
    <skill-name>.yaml         ← one promptfoo config per skill (13 total)
    provider.py               ← response provider: llamacpp HTTP at localhost:8080
    grader.py                 ← judge provider: llamacpp HTTP at localhost:8080
    scaffold_helper.py        ← shared project scaffolding logic
    provider_pi.py            ← alternative pi-CLI provider (reference only)
.claude-plugin/
  plugin.json                ← registered skill list
  link-skills.sh             ← symlinks skills/ into ~/.claude/skills/
scripts/
  link-skills.sh             ← same as .claude-plugin/link-skills.sh
  list-skills.sh             ← lists all skills in collection
```

Root `SKILL.md` is absent by design — `npx skills` discovers skills from bucket subfolders.

## Running Evals

Requires `promptfoo` on PATH and a llamacpp server running at `localhost:8080`.
Both the response model and the LLM judge use the server (see `provider.py` / `grader.py`).

```bash
# All skills:
python evals/run_evals.py

# One skill only:
python evals/run_evals.py --skill harness-audit

# Filter to specific evals (regex matched against description):
python evals/run_evals.py --skill harness-audit --filter "#2"

# Run promptfoo directly for a skill:
cd evals/promptfoo && promptfoo eval --config harness-audit.yaml
```

The runner:
1. Discovers all `evals/promptfoo/<skill>.yaml` configs
2. Invokes `promptfoo eval --config <skill>.yaml --no-cache` per skill
3. The provider scaffolds a minimal project temp dir and calls llamacpp HTTP
4. The grader judges each assertion via a separate llamacpp HTTP call

Model and API base are set in `evals/promptfoo/provider.py` (`MODEL`, `API_BASE`).

**Before committing any change to a skill file, run `python evals/run_evals.py --skill <name>` and confirm all evals pass.**

## Skill Flow Architecture

The skill runs in three phases (defined in `SKILL.md`):

1. **Phase 1 — Detect**: Runs 10 checks against the live project (hooks, stack, CI, pre-commit, init.sh, instruction file, rules dir, spec workflow, UI harness, installed skills). Builds complete gap list before any output.
2. **Phase 2 — Interview**: Asks at most 3 questions (task scope, team size, priority) to resolve what file scanning can't determine. Each question waits for an answer.
3. **Phase 3 — Output**: Produces "Already in place" + prioritised gap list (max 5 gaps) with complete paste-ready snippets. Stop hook is ALWAYS gap #1 when `.claude/settings.json` is absent.

## Key Invariants

- **Stop hook is always gap #1** when `.claude/settings.json` is missing — no other gap may precede it.
- **AGENTS.md is fully equivalent to CLAUDE.md** — never flag missing CLAUDE.md when AGENTS.md is present; never recommend creating both.
- **Brownfield codebase**: never tell users to fix all lint errors manually. Recommend `eslint --fix` in a single cleanup commit (ratchet approach).
- **Multi-day scope**: output MUST include "one active task at a time", at least one verification anti-pattern by name (Fuzzy Done / Proxy Signal / Confidence Exit / Planning=Done), and a Judge audit as the exit criterion.
- Each snippet must be complete and paste-ready — no `YOUR_PROJECT_NAME` placeholders.

## Editing Conventions

- Skill content lives in `SKILL.md` and `references/*.md`. `evals/evals.json` captures acceptance criteria in legacy format; `evals/promptfoo/<skill>.yaml` is the canonical eval definition.
- Snippets are not duplicated between reference files — stack-specific content belongs in `node-snippets.md` or `python-snippets.md`, not in `universal-snippets.md`.
- Every gate recommendation in `SKILL.md` must justify itself with a failure mode (one sentence). No failure mode = don't add it.
- When adding a new eval scenario, add it to `evals/promptfoo/<skill>.yaml` first, then update `SKILL.md` to cover it.

## Global Constraints

- **KISS** — prefer the simplest solution. If a simpler path exists, say so before implementing.
- **YAGNI** — no features, abstractions, or flexibility beyond what was asked.
- **DRY** — shared logic in one place. Snippets don't duplicate content across helper files.
- **First Principles** — every gate must justify itself with a failure mode in one sentence.
- **Occam's Razor** — when two solutions close the same gap, prefer fewer moving parts.

## Agent skills

Install via `bash scripts/link-skills.sh`. Invoke with `/skill-name`.

### Engineering
| Skill | Purpose |
|---|---|
| `harness-audit` | Detect harness gaps and output paste-ready fix snippets |
| `setup-harness-skills` | One-time project harness configuration |
| `context-handover` | Package session context for handoff to next session |
| `session-start` | Resume from last session state in `.planning/STATE.md` |
| `triage` | Triage GitHub issues with canonical labels |
| `to-prd` | Convert conversation context into a PRD issue |
| `to-issues` | Break a PRD into scoped GitHub issues |
| `zoom-out` | Step back and reframe current work |
| `grill-with-docs` | Stress-test a plan against domain docs and ADRs |

### Productivity
| Skill | Purpose |
|---|---|
| `caveman` | Simplify ideas to first principles |
| `grill-me` | Interview-style plan stress-test |
| `handoff` | Compact conversation into a handoff document |
| `write-a-skill` | Create a new agent skill with proper structure |
