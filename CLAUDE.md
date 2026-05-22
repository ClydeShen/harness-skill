# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo maintains the `harness-engineering` skill — an interactive diagnostic tool that detects harness gaps in a project and produces paste-ready config snippets to close them. It is packaged as a Claude Code / Codex marketplace plugin.

## Skill Structure

```
skills/harness-engineering/
  SKILL.md                   ← main skill: detect → interview → output flow
  skill.json                 ← skill metadata (name, version, tags)
  evals/
    evals.json               ← acceptance criteria for all 6 eval prompts
  references/
    detect.md                ← gap classification and detection interpretation
    universal-snippets.md    ← .claude/settings.json, init.sh, CI, CLAUDE.md template
    node-snippets.md         ← Node/TS paste-ready configs
    python-snippets.md       ← Python paste-ready configs
```

Root `SKILL.md` stays intentionally empty (see README).

## Running Evals

```bash
python run_evals.py
```

Requires `claude` CLI on PATH with an active session. The runner:
1. Copies the skill to an isolated temp dir (avoids git repo leakage into eval workspace)
2. Scaffolds a minimal project per eval (package.json, ci.yml, CLAUDE.md stubs, etc.)
3. Runs each eval prompt via `claude -p --plugin-dir <isolated> --model sonnet`
4. Judges each expectation via a separate `claude -p --model haiku` call (PASS/FAIL)

Models: `RESPONSE_MODEL = "sonnet"`, `JUDGE_MODEL = "haiku"` — change at the top of `run_evals.py`.

**Before committing any change to a skill file, run evals and confirm all 6 pass.**

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

- Skill content lives in `SKILL.md` and `references/*.md`. `evals.json` defines acceptance criteria.
- Snippets are not duplicated between reference files — stack-specific content belongs in `node-snippets.md` or `python-snippets.md`, not in `universal-snippets.md`.
- Every gate recommendation in `SKILL.md` must justify itself with a failure mode (one sentence). No failure mode = don't add it.
- When adding a new eval scenario, add it to `evals.json` first, then update `SKILL.md` to cover it.

## Global Constraints

- **KISS** — prefer the simplest solution. If a simpler path exists, say so before implementing.
- **YAGNI** — no features, abstractions, or flexibility beyond what was asked.
- **DRY** — shared logic in one place. Snippets don't duplicate content across helper files.
- **First Principles** — every gate must justify itself with a failure mode in one sentence.
- **Occam's Razor** — when two solutions close the same gap, prefer fewer moving parts.
