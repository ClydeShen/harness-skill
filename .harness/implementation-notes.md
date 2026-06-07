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

## 2026-06-07 — Skill-set Fuller analysis + harness-verify-before-move confidence labels

Ran a Fuller-style (whole-system, Socratic) review of the skill set at the user's request, focused on whether `harness-triage`, `harness-verify-before-move`, and related skills hold a consistent standard. Three conclusions reached and acted on:

1. **`harness-triage` needs no behavioral change.** Initial read suggested its workflow might mismatch how the rest of the harness reports state, but tracing its actual triage logic against `harness-issues` and the GitHub sync flow showed the apparent mismatch was a difference in *purpose* (triage classifies new issues; it doesn't report on phase-exit state), not a inconsistency to fix. No edit applied.

2. **Root cause of `harness-verify-before-move` incompleteness: uniform pass/fail collapses verified/assumed/skipped states.** The skill's 10-step sweep reported a flat pass/fail per step, which let an agent claim "Code: pass" when it had only inferred the result (e.g., "tests probably still pass") rather than directly observed it (ran the command, read the output). This is the same Fuzzy-Done/Proxy-Signal/Confidence-Exit failure the skill itself is supposed to catch — just one level up, in its own self-reporting.

   **Fix applied — 3 edits to `skills/engineering/harness-verify-before-move/SKILL.md`:**
   - Added a confidence-label contract before the step sequence: every step's summary line must be prefixed with exactly one of `[VERIFIED]` / `[ASSUMED]` / `[SKIPPED — <reason>]`, with explicit definitions for each (direct evidence vs. inference vs. missing precondition) and an instruction not to default to `[VERIFIED]`.
   - Rewrote the Step 10 GitHub progress-comment template and the final user-facing snapshot template to carry per-area `[VERIFIED]`/`[ASSUMED]`/`[SKIPPED — reason]` labels (Code, Phase gates, Design docs, Implementation notes, Unused documents, Memory, GitHub, README) instead of a single uniform "all green" block — including a top-line confidence tally (`N verified · N assumed · N skipped`) and inline guidance that every `[ASSUMED]`/`[SKIPPED]` line must name what wasn't directly checked and why.
   - Added a closing instruction tying this back to the Step 1 anti-pattern table: a step that silently downgrades to "looks fine" without naming that downgrade is committing the exact Fuzzy-Done/Proxy-Signal/Confidence-Exit pattern the skill exists to catch in the user's work.

3. **Decision: encode the fix as a meta-rule in `write-harness-skill`, not a shared `references/status-vocabulary.md`.** Initially considered extracting the verified/assumed/skipped vocabulary into a shared reference file other skills could point to. The user corrected this — skills in this collection are installed and distributed independently (via `npx skills add`), and this repo's `CLAUDE.md`/shared references do not travel with an individually-installed skill. A cross-file reference would silently break for any skill installed standalone. The right place to encode "skills that report on state must distinguish verified/assumed/unchecked" is the **review checklist in `write-harness-skill`** — a self-contained authoring-time gate that travels with the skill being authored, not a runtime dependency on this repo's structure.

### Remaining work from this session (not yet done)
- Lower priority, not yet requested: doc drift fixes (skill count "14"→12, README "Five skills"→7 rows, version v2.6.0→v2.7.0), a `fuller` eval file, optional `harness-triage` doc note about workflow-purpose distinction.

### 2026-06-07 (cont'd) — meta-rule + eval written, eval run interrupted

Completed the two items queued above:
- Added the meta-rule to `skills/productivity/write-harness-skill/SKILL.md` Review Checklist (new bullet after the issue-creation-gates item): "If the skill reports on the state of something ... does it distinguish `[VERIFIED]` / `[ASSUMED]` / `[SKIPPED — reason]` rather than collapsing to a uniform pass signal?"
- Created `evals/promptfoo/harness-verify-before-move.yaml` with 6 scenarios covering: confidence labels present, `[ASSUMED]` vs `[VERIFIED]` distinction, BLOCK at Step 1, graceful degradation with no `state.json`, destructive-ops confirmation, and GitHub-sync skip labelling.

**Bug found and fixed in the new eval file:** first run produced 19 test cases instead of 6 and 14/19 failed — `scaffold_files` was written as a YAML list, which promptfoo expands into one test case per list item (each test then got only ONE scaffold file instead of the full set). Fixed by switching to the JSON-string format that `context-handover.yaml` already uses (`scaffold_files: '["file1", "file2", ...]'`), which provider.py parses back into a list without expansion. Re-run against local llamacpp confirmed the fix: 6 test cases produced (matching the 6 yaml entries).

**Status: eval run NOT yet confirmed passing — CLAUDE.md gate still open.** User asked to switch the eval provider from local llamacpp to NVIDIA's cloud API (`meta/llama-3.3-70b-instruct`, via `EVAL_API_BASE`/`EVAL_API_KEY`/`EVAL_PROVIDER_MODEL` already present in `.env.local` from the separate eval-haiku-harness-issues thread). Started that run but the user interrupted it mid-flight ("先停止，我发现有个skill要改一点细节") to go make a small edit to a skill first. The run was killed (no partial results captured — promptfoo only writes the results table at completion).

**Next action:** after the user's skill-detail edit lands, re-run `python evals/run_evals.py --skill harness-verify-before-move` (with NVIDIA env vars sourced from `.env.local`) and confirm all 6 scenarios pass before committing — per the CLAUDE.md gate "Before committing any skill change: run the evals and confirm all pass."
