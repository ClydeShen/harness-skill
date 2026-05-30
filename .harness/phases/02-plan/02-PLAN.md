# PLAN.md — Skill Evals Integration Harness

Spec: docs/superpowers/specs/2026-05-29-skill-evals-integration-harness-design.md
Branch: feature/eval-integration-harness
Issues: #14, #15, #16, #17

---

## Task 1: Fix session-start stale schema (#14)

**Type:** chore
**Effort:** 1 context window(s)

### What to build
Replace all `.harness/STATE.md` and `.continue-here.md` fixture references in session-start.yaml with the current schema (`.harness/state.json`, `.continue-here.json`). Add regression not-icontains guards for old paths. Update scaffold_helper.py to scaffold state.json and .continue-here.json.

### Acceptance criteria
- [ ] session-start.yaml has no STATE.md or .continue-here.md fixture strings
- [ ] scaffold_helper.py scaffolds .harness/state.json with correct schema
- [ ] scaffold_helper.py scaffolds .harness/phases/XX/.continue-here.json
- [ ] Regression not-icontains asserts block .harness/STATE.md in model output

---

## Task 2: Add provider_artifact.py and assertion helpers (#15)

**Type:** feature
**Effort:** 2 context window(s)

### What to build
New provider_artifact.py that builds temp workspace from structured fixtures, extracts artifact-json blocks from model output, applies file writes, and returns files_before/files_after/changed_files. New evals/promptfoo/assertions/__init__.py with deterministic Python helpers.

### Acceptance criteria
- [ ] provider_artifact.py implements call_api with structured fixture support
- [ ] artifact-json block parsed and applied to temp workspace
- [ ] assertions/__init__.py exports file_exists, json_has_keys, no_stale_paths, gh_call_sequence
- [ ] scaffold_helper.py updated to support state.json and .continue-here.json fixtures

---

## Task 3: Add skill-cleanup eval config (#16)

**Type:** feature
**Effort:** 1 context window(s)

### What to build
New evals/promptfoo/skill-cleanup.yaml with 5+ test cases covering stale skill detection, dry-run, confirmation gate, orphan detection, and removal sequence.

### Acceptance criteria
- [ ] skill-cleanup.yaml exists with at least 5 test cases
- [ ] Each case tests a distinct scenario from Spec §6
- [ ] Config uses existing provider.py (text contract tier)

---

## Task 4: Add --tier flag to run_evals.py (#17)

**Type:** feature
**Effort:** 1 context window(s)
**Blocked by:** Task 2 (#15)

### What to build
Add --tier text|artifact|external flag to run_evals.py. Default runs text+artifact. Each yaml gets an optional tier: metadata field that run_evals.py reads to filter.

### Acceptance criteria
- [ ] --tier text runs only text-tier configs
- [ ] --tier artifact runs only artifact-tier configs
- [ ] No --tier runs text+artifact (default)
- [ ] Files without tier metadata treated as text tier (backwards compatible)
