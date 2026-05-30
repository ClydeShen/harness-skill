# Implementation Notes — Eval Integration Harness

## Decisions made not in spec

- **provider_artifact.py max_tokens set to 1024** (vs provider.py's 512): artifact evals need more output to include the artifact-json block.
- **`no_stale_paths` default list is conservative**: only checks STATE.md and .continue-here.md, not .claude/session.json, to avoid false positives in existing fixtures that legitimately scaffold session.json for other skill tests.
- **`--tier` default includes both text + artifact** (not text only): the spec says "keep default local run to text + artifact", so running without --tier runs both.
- **Backward compat**: yaml files without `# tier:` comment are treated as `text` tier so existing configs (harness-audit, harness-guide, etc.) continue to run with no changes.
- **skill-cleanup.yaml uses provider.py** (text tier): the skill produces prose + commands, not JSON files, so artifact provider not needed for first-pass coverage.

## Changes from original plan

- Skipped Phase 3 (fake gh provider / provider_gh_fake.py): too complex for KISS first pass. The spec marks it as "deferred" for multi-turn flows and notes the fake executable fallback is optional. Issues #14-17 cover Phases 1, 2, 4, 5 only.
- `session-start.yaml` removed eval #5 (no prior session that wrote session_status to STATE.md) because it referenced the stale state machine directly — merged its intent into eval #1's rubric about briefing ordering.

## Tradeoffs

- **Artifact-json block approach**: less realistic than actual file tool execution but immediately closes the "prose only" gap as spec intends. The artifact block is a machine-readable trailer, hidden from rubric grading by stripping it before passing output to the judge.
- **Assertions module is import-only**: promptfoo type:python assertions can call the helpers but the module isn't auto-discovered — each assertion must `from assertions import ...` explicitly.
