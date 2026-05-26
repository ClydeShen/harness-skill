# Eval Report — 2026-05-26

Full promptfoo eval run across all 13 skills via llamacpp (qwen2.5-coder-32b-instruct-q5_k_m @ localhost:8080).

## Score Summary

| Skill | Pass | Fail | Total | Rate |
|---|---|---|---|---|
| zoom-out | 3 | 0 | 3 | 100% |
| write-a-skill | 1 | 1 | 2 | 50% |
| harness-engineering | 21 | 15 | 36 | 58% |
| handoff | 2 | 3 | 5 | 40% |
| session-start | 1 | 5 | 6 | 17% |
| setup-harness-skills | 1 | 6 | 7 | 14% |
| caveman | 0 | 2 | 2 | 0% |
| context-handover | 0 | 5 | 5 | 0% |
| grill-me | 0 | 4 | 4 | 0% |
| grill-with-docs | 0 | 4 | 4 | 0% |
| to-issues | 0 | 5 | 5 | 0% |
| to-prd | 0 | 5 | 5 | 0% |
| triage | 0 | 6 | 6 | 0% |
| **TOTAL** | **29** | **61** | **90** | **32%** |

---

## Root Cause Analysis

### Class A — Eval infrastructure (not skill defects)

The scaffold_helper creates files by name only. A scaffold_files entry like
`".claude/session.json with execution phase and github issue 7"` becomes an empty file
with that literal string as its filename. Skills that read file content (session-start,
context-handover, setup-harness-skills) cold-start because they find no parseable content.

Affects: session-start (5/6 failures), context-handover (5/5), setup-harness-skills (5/6).

**Fix:** scaffold_helper.py should recognise well-known file patterns and write real content
(parseable JSON for session.json, valid markdown for handoff.md, N-line stubs for CLAUDE.md).

### Class B — Multi-turn skills tested single-turn

grill-me, grill-with-docs, and bare write-a-skill are sequential by design. In one shot the
model produces a multi-question summary instead of a single question, tripping the
"asks one at a time" assertions. These can't pass without a conversation loop.

Affects: grill-me (4/4), grill-with-docs (4/4), write-a-skill eval #1.

**Fix:** Reframe assertions to test first-response shape only ("first response contains
exactly one question"), or invest in multi-turn eval infrastructure.

### Class C — External service dependencies

triage, to-issues, and to-prd require a live issue tracker or real codebase context.
With no `gh` configured and empty scaffold files, triage correctly says "no issues to
triage" and to-prd invents a fictional project.

Affects: triage (6/6), to-issues (5/5), to-prd (5/5).

**Fix:** Scaffold files need mock content — a fake issues list JSON for triage,
a real PRD stub for to-issues, existing feature code stubs for to-prd.

---

## Real Skill Defects (fixable in SKILL.md)

### harness-engineering — eval #9 (already-configured, not-icontains fails)

Model correctly recognises `docs/agents/` as already in place but still outputs
`/setup-harness-skills` elsewhere, tripping the `not-icontains` assertion.

**Fix:** Strengthen the negative instruction in SKILL.md:
> "Never mention `/setup-harness-skills` at all if all five docs/agents/ files are present."

### harness-engineering — eval #5 (brownfield, eslint --fix missing)

Model flags brownfield and recommends the Stop hook, but doesn't consistently mention
`eslint --fix` as the bulk approach. The grader fails "Suggests an automated/bulk approach".

**Fix:** Brownfield section should say:
> "Recommend `eslint --fix .` in a single cleanup commit. Never suggest manual fixes."

### harness-engineering — eval #4 (multi-gap, scaffold design issue)

The eval creates 5 separate test cases (one per scaffold_file line in the YAML list),
but the prompt describes all files simultaneously. Each test case only sees one file,
causing assertion mismatches.

**Fix:** Collapse the 5 scaffold_file lines into a single test case with all files together.

### triage — eval #3 (quick override, confirm-before-act missing)

Response asks about the agent brief but doesn't first confirm ALL intended actions
(role change + comment). The SKILL.md says "Confirm what you're about to do, then act"
but the model skips straight to asking about the brief.

**Fix:** Make the confirm step explicit and ordered: confirm all actions first, then ask about brief.

---

## Pre-run Fixes Applied

Before running, 4 issues were corrected:

1. `write-a-skill.yaml` eval #2 — threshold corrected from 100 → 500 lines
2. `harness-engineering.yaml` eval #7 (Kiro) — added `icontains: "Kiro"` deterministic check
3. `harness-engineering.yaml` eval #8 (Gemini) — added `icontains: "GEMINI.md"` deterministic check
4. `provider_pi.py` — refactored to skill-generic (reverted to provider.py when pi backend
   timed out: model name mismatch, pi configured for qwen3.6 but server runs qwen2.5-coder-32b)

---

## Recommended Fix Order

1. `scaffold_helper.py` — real content for session.json, handoff.md, CLAUDE.md stubs
2. `harness-engineering.yaml` eval #4 — collapse 5 scaffold variants into one multi-file test
3. `harness-engineering/SKILL.md` — harden brownfield and already-configured guard
4. `triage/SKILL.md` — explicit confirm-all-actions before quick override
5. grill-me / grill-with-docs evals — reframe assertions to first-response shape only
