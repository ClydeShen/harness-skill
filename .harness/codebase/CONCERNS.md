# Concerns
_Generated: 2026-05-27_

## Technical Debt

**Dual config-file schema (harness.json vs .harness/config.json):**
`setup-harness-skills` writes `.claude/harness.json` in Step 2 of `output-steps.md`, but `SKILL.md` line 27 also marks `.claude/harness.json` as deprecated and describes a migration path to `.harness/config.json`. Skills `session-start`, `context-handover`, `harness-audit`, and `harness-guide` all reference `.harness/config.json` as the canonical location, yet `output-steps.md` and `session-config.md` still document `.claude/harness.json` as the authoritative schema with "Written by: setup-harness-skills". The migration is described in prose but is not enforced — new installs via `setup-harness-skills` still produce `.claude/harness.json`. Any project set up after the migration announcement will have a stale `.claude/harness.json` that skills read as legacy fallback, creating silent discrepancies.
- Files: `skills/engineering/setup-harness-skills/output-steps.md`, `skills/engineering/setup-harness-skills/session-config.md`, `skills/engineering/setup-harness-skills/SKILL.md`
- Fix approach: Update `output-steps.md` Step 2 to write `.harness/config.json` harness namespace directly instead of `.claude/harness.json`. Deprecate `session-config.md`'s harness.json schema section and point readers at the config.json schema. Remove legacy fallback references from session-start and context-handover once migration is complete.

**Legacy `.claude/session.json` still documented and supported:**
`session-config.md` documents `.claude/session.json` with a full schema, and `context-handover/SKILL.md` line 93 still writes `last_handover`/`next_session_hint` back to `session.json`. `session-start/SKILL.md` lists `.claude/session.json` as a fallback on the explore step. The `.gitignore` gitignores it. There is no mechanism to detect when migration to `.harness/STATE.md` is complete and stop writing to the legacy path.
- Files: `skills/engineering/setup-harness-skills/session-config.md`, `skills/engineering/context-handover/SKILL.md`, `skills/engineering/session-start/SKILL.md`
- Fix approach: Add a migration gate — if `.harness/STATE.md` exists, stop writing `session.json`. Mark `session-config.md` as "legacy reference only".

**`skill.json` only present for two of ten engineering skills:**
Only `harness-audit` and `harness-guide` have a `skill.json`. The remaining eight engineering skills (`setup-harness-skills`, `context-handover`, `session-start`, `triage`, `to-prd`, `to-issues`, `zoom-out`, `grill-with-docs`) and all five productivity skills lack this metadata file. `plugin.json` declares all 15 skills without relying on `skill.json`, so this has no runtime impact, but it creates inconsistent structure and makes skills not independently publishable via skills.sh per-skill install.
- Files: All skill directories under `skills/engineering/` and `skills/productivity/` except `harness-audit/` and `harness-guide/`
- Fix approach: Either add `skill.json` to every skill (copy schema from `harness-audit/skill.json`) or document that `skill.json` is optional and only required for top-level published skills.

**`node_modules/` committed inside `skill-cleanup`:**
`skills/productivity/skill-cleanup/node_modules/` is tracked in the repository. The root `.gitignore` ignores `node_modules/` at repo root but not inside subdirectories. This inflates repo size and causes diffs when dependencies update.
- Files: `skills/productivity/skill-cleanup/node_modules/` (entire subtree)
- Fix approach: Add `skills/productivity/skill-cleanup/node_modules/` to `.gitignore`. Confirm `package.json` and `package-lock.json` are committed so users can run `npm install` after cloning.

**CLAUDE.md describes 14 skills but 15 are registered in plugin.json:**
`CLAUDE.md` line 8 states "All 14 skills implemented" and the Engineering/Productivity tables list 14 skills. `plugin.json` registers 15 (includes `skill-cleanup`). `README.md` says "Full Collection (all 15 skills)". The count in `CLAUDE.md` is stale.
- Files: `CLAUDE.md`, `.claude-plugin/plugin.json`, `README.md`
- Fix approach: Update `CLAUDE.md` skill count and table to include `skill-cleanup`.

---

## Risks

**10 of 15 skills have no promptfoo eval coverage:**
Only `harness-audit`, `harness-guide`, `context-handover`, `session-start`, and `setup-harness-skills` have `evals/promptfoo/*.yaml` configs. The following skills have only legacy `evals/evals.json` entries (not wired into `run_evals.py`) or no evals at all:
- `triage` — legacy `evals.json` only, no promptfoo config
- `to-prd` — legacy `evals.json` only, no promptfoo config
- `to-issues` — legacy `evals.json` only, no promptfoo config
- `zoom-out` — legacy `evals.json` only, no promptfoo config
- `grill-with-docs` — legacy `evals.json` only, no promptfoo config
- `caveman` — no evals at all
- `grill-me` — no evals at all
- `handoff` — no evals at all
- `write-a-skill` — no evals at all
- `skill-cleanup` — no evals at all

`run_evals.py` discovers configs from `evals/promptfoo/*.yaml` only — the legacy `evals/evals.json` files are unreachable from the runner. Behavioral regressions in these 10 skills go completely undetected by CI.
- Files: `evals/run_evals.py`, `evals/promptfoo/` (missing yaml files), `skills/engineering/*/evals/evals.json`

**CI only validates promptfoo schema and Python syntax — no behavioral gate:**
`.github/workflows/ci.yml` runs `npm run eval:validate` (schema validation) and `python -m py_compile` (syntax check). It does not run `python evals/run_evals.py` or any promptfoo evals. Behavioral regressions in even the 5 covered skills will not be caught before merge unless a developer manually runs the eval suite. The eval system requires a local llamacpp server at `localhost:8080`, making it impractical to run in GitHub Actions without significant infra work.
- Files: `.github/workflows/ci.yml`, `evals/promptfoo/provider.py`

**`sync-status.yml` hardcodes project board IDs:**
`.github/workflows/sync-status.yml` hardcodes `PROJECT_ID: PVT_kwHOAPZRDM4BYnKy`, `STATUS_FIELD_ID: PVTSSF_lAHOAPZRDM4BYnKyzhTrw68`, `OWNER: ClydeShen`, and `REPO: harness-skill`. Contributors who fork the repo will receive workflow failures or silent no-ops when these IDs do not match their project board. There is no guard or informational failure.
- Files: `.github/workflows/sync-status.yml`

**`context-handover` GitHub comment references deprecated `.claude/handoff.md` path:**
The GitHub handover comment template in `context-handover/SKILL.md` line 87 still shows `**Handoff doc:** '.claude/handoff.md'` — the old pre-migration path. The actual handoff doc is now written to `.harness/phases/XX-name/.continue-here.md`. A session resuming from the GitHub comment would look in the wrong location.
- Files: `skills/engineering/context-handover/SKILL.md`

**`setup-harness-skills` output-steps.md writes `.claude/harness.json` but SKILL.md gitignore block omits it:**
`output-steps.md` line 117 states "`.claude/harness.json` is NOT gitignored — it is committed as shared team config." But the `.gitignore` additions block in `SKILL.md` only adds `.harness/phases/*/.continue-here.md`. If a developer follows the SKILL.md output section rather than reading output-steps.md, `.claude/harness.json` may not be committed.
- Files: `skills/engineering/setup-harness-skills/SKILL.md`, `skills/engineering/setup-harness-skills/output-steps.md`

---

## Known Issues

**`evals/evals.json` format is unreachable by the eval runner:**
CLAUDE.md line 105 states "`evals/evals.json` captures acceptance criteria in legacy format; `evals/promptfoo/<skill>.yaml` is the canonical eval definition." However, `run_evals.py` has no code to read or run legacy `evals.json` files. They exist as documentation artifacts but provide no CI enforcement. For the 5 skills that have both formats, the `evals.json` and the `.yaml` have diverged (e.g., `to-prd`'s `evals.json` checks for "Technical Constraints" section, the SKILL.md was since renamed to "Implementation Decisions"). The legacy files actively mislead future contributors about what is tested.
- Files: `skills/engineering/*/evals/evals.json`

**`to-prd/SKILL.md` uses "Technical Constraints" label in the prd-template but `evals/evals.json` checks for it while SKILL.md has renamed the section to "Implementation Decisions" (GSD CONTEXT.md format):**
The prd-template section still uses "Technical Constraints" as the section header. `evals/evals.json` eval #1 checks for "Problem Statement, Solution, User Stories, Implementation Decisions" — a mismatch with the template's actual header. The PRD template and the dual output (GitHub issue vs GSD CONTEXT.md format) create ambiguity about what the canonical output is.
- Files: `skills/engineering/to-prd/SKILL.md`

**`setup-harness-skills` Step 2 writes to `.claude/harness.json` but SKILL.md migration section says to write to `.harness/config.json`:**
These are contradictory instructions in the same skill's files. An agent following `output-steps.md` will create `.claude/harness.json`. An agent reading the migration section of `SKILL.md` will write to `.harness/config.json`. There is no authoritative signal about which is current.
- Files: `skills/engineering/setup-harness-skills/output-steps.md` (Step 2), `skills/engineering/setup-harness-skills/SKILL.md` (lines 90, 103)

**`harness-audit` Check #8 refers to `docs/agents/` but `setup-harness-skills` `output-steps.md` uses the same directory name via `session-config.md` which lists it under a deprecated `harness.json` schema:**
The five files expected by `harness-audit` Check #8 (`issue-tracker.md`, `triage-labels.md`, `domain.md`, `github-project.md`, `session-config.md`) match the files written in `output-steps.md` Step 9. However, `session-config.md` (the file written to `docs/agents/`) describes the deprecated `.claude/session.json` schema, not the current `.harness/STATE.md` + `.harness/config.json` schema. Skills reading this seed file will receive outdated configuration guidance.
- Files: `skills/engineering/setup-harness-skills/session-config.md`, `skills/engineering/harness-audit/SKILL.md`

---

## Improvement Opportunities

**Migrate legacy `evals/evals.json` files to promptfoo format for the 5 engineering skills that have them:**
`triage`, `to-prd`, `to-issues`, `zoom-out`, and `grill-with-docs` each have legacy `evals/evals.json`. Converting these to `evals/promptfoo/<skill>.yaml` format would bring them under `run_evals.py` CI coverage and follow the documented canonical format. The existing expectations in each `evals.json` provide a starting point for scenario descriptions.
- Files: `evals/promptfoo/` (missing: `triage.yaml`, `to-prd.yaml`, `to-issues.yaml`, `zoom-out.yaml`, `grill-with-docs.yaml`)

**Add promptfoo evals for the 5 skills with no evals at all:**
`caveman`, `grill-me`, `handoff`, `write-a-skill`, and `skill-cleanup` have no eval coverage of any kind. Observable behaviors to test: caveman mode persistence across turns, grill-me sequential questioning (one question at a time), handoff writing to OS temp dir and not the workspace, write-a-skill creating the correct file structure and checking description length.
- Files: `evals/promptfoo/` (missing: `caveman.yaml`, `grill-me.yaml`, `handoff.yaml`, `write-a-skill.yaml`, `skill-cleanup.yaml`)

**Add `skill.json` to all skills for consistent structure and skills.sh compatibility:**
Only `harness-audit` and `harness-guide` have `skill.json`. Adding it to the remaining 13 skills creates a consistent structure and allows individual skills to be published or installed via `npx skills add` per-skill.
- Files: All skill directories lacking `skill.json`

**Consolidate session-config.md to document current schema only:**
`session-config.md` documents both the legacy `.claude/session.json` and the current `.harness/STATE.md` + `.harness/config.json` approach on the same file. Splitting into a clearly labelled "legacy" section vs "current" section — or removing the `.claude/session.json` schema entirely once migration is confirmed — would reduce confusion.
- Files: `skills/engineering/setup-harness-skills/session-config.md`

**`write-a-skill` review checklist could enforce consistency across this repo's own skills:**
`write-a-skill/SKILL.md` includes a review checklist that checks for token budget mention, `setup-harness-skills` reference when reading config, and AI-generated footer on issue tracker posts. Several skills in this repo do not satisfy these checks (e.g., `handoff` has no token budget note, `zoom-out` has no `setup-harness-skills` reference despite working with project context). Running the checklist against all skills periodically would surface these gaps.
- Files: `skills/productivity/write-a-skill/SKILL.md`

---

## Coverage Gaps

**No eval coverage for multi-turn / iterative behavior:**
`harness-guide` is designed as a coaching loop (re-run Phase 1 on each iteration), but all 5 of its evals are single-turn. The iterative behavior — "after user acts on recommendation, re-classify" — is entirely untested. A regression where `harness-guide` gives the same recommendation twice rather than updating its classification would not be caught.
- Files: `evals/promptfoo/harness-guide.yaml`

**No integration eval between `context-handover` and `session-start`:**
`session-start` eval #4 is labelled "Integration eval: tests session-start reading context-handover's state machine output" but it scaffolds a pre-built STATE.md fixture rather than actually running `context-handover` first. A true integration path where `context-handover` writes STATE.md and `.continue-here.md` and `session-start` reads it is not covered end-to-end.
- Files: `evals/promptfoo/session-start.yaml`

**`harness-audit` eval #16 (hooks JSON schema) was added after #15 but numbered out of sequence:**
Evals are numbered 1–15 but eval #16 appears between #15 (skill collections) and #15 (skill collections re-numbered) in `harness-audit.yaml`. The numbering jump from #14 to #16 to #15 at the end of the file is confusing and could cause issues if the `--filter "#15"` flag is used — it would match both the hooks schema eval and the collections eval.
- Files: `evals/promptfoo/harness-audit.yaml`

**No eval for `setup-harness-skills` migration path (`.claude/harness.json` → `.harness/config.json`):**
`setup-harness-skills` has 4 evals covering new project setup, update of existing harness, no instruction file, and GSD already installed. None of them test the migration scenario described in `SKILL.md` — detecting `.claude/harness.json`, migrating its values to `.harness/config.json`, and confirming before deleting old files.
- Files: `evals/promptfoo/setup-harness-skills.yaml`

**`grill-with-docs` has no eval for CONTEXT.md update behavior:**
The skill's core differentiator — updating `CONTEXT.md` inline as terms are resolved — is entirely untested. There is no eval that verifies term capture, avoidance of implementation details in CONTEXT.md, or the ADR creation criteria (hard to reverse, surprising without context, genuine trade-off).
- Files: `skills/engineering/grill-with-docs/evals/evals.json` (legacy, not running)

**`triage` has no eval for the `wontfix` flow including `.out-of-scope/` knowledge base:**
`triage/SKILL.md` describes writing rejected enhancements to `.out-of-scope/` and linking from a comment, but none of the 3 legacy evals cover this path. The `OUT-OF-SCOPE.md` reference file documents the knowledge base format, but its usage by the skill is unverified.
- Files: `skills/engineering/triage/evals/evals.json`, `skills/engineering/triage/OUT-OF-SCOPE.md`
