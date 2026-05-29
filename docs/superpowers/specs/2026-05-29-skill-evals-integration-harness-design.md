# Skill Evals Integration Harness Design

**Date:** 2026-05-29
**Status:** Draft for review

## Problem

The current promptfoo evals mostly test whether a model can describe the right skill behavior. That is useful for advisory skills, but it is too weak for skills whose outcome is a changed project state.

Examples:

- `context-handover` is expected to write `.harness/state.json` and `.harness/phases/*/.continue-here.json`, but current evals only ask an LLM judge whether the response says those files were written.
- `session-start` evals still use stale `.harness/STATE.md` and `.continue-here.md` fixtures, while the current skills use `.harness/state.json` and `.continue-here.json`.
- `setup-harness-skills`, `harness-triage`, and `harness-issues` describe GitHub mutations, but no eval captures whether the expected `gh` operations would happen in the right order.
- `skill-cleanup` is registered in the plugin but has no promptfoo eval config.

The result is a false sense of coverage: a skill can pass by producing plausible prose while failing to create the artifacts, schemas, or external-system calls that define its real outcome.

## Goal

Create a slightly heavier integration eval harness that keeps promptfoo as the orchestration layer but adds deterministic checks for:

- file artifacts
- JSON schema and path conventions
- mocked GitHub CLI calls
- issue and board mutation ordering
- stale-schema regression guards

The harness should make each eval answer this question: **did the skill outcome happen, not merely get described?**

## Non-Goals

- Do not hit live GitHub in evals.
- Do not require Claude Code, Codex Desktop, or any interactive agent runtime to run the core eval suite.
- Do not replace `llm-rubric` entirely; it remains useful for text-heavy skills.
- Do not build a full multi-turn conversation simulator in the first iteration.

## Eval Layers

### Layer 1: Text Contract Evals

These remain close to the current promptfoo setup. They validate ordering rules, required phrases, forbidden phrases, and document structure.

Use for:

- `harness-audit`
- `harness-guide`
- `harness-prd`
- `write-harness-skill`

Assertions:

- `contains`
- `icontains`
- `not-icontains`
- `is-json`
- `llm-rubric`
- `latency`

Outcome examples:

- Stop hook is listed as gap #1.
- AGENTS.md is treated as equivalent to CLAUDE.md.
- Brownfield lint guidance recommends bulk fixes, not manual cleanup.
- PRD keeps WHAT constraints separate from HOW implementation details.

### Layer 2: Artifact Evals

Add a provider that creates a temporary workspace, runs the skill prompt against the model, captures intended or actual file outputs, and returns a structured payload:

```json
{
  "output": "model response",
  "files_before": {
    ".harness/state.json": "{...}"
  },
  "files_after": {
    ".harness/state.json": "{...}",
    ".harness/phases/03-execute/.continue-here.json": "{...}"
  },
  "changed_files": [
    ".harness/state.json",
    ".harness/phases/03-execute/.continue-here.json"
  ],
  "commands": [],
  "errors": []
}
```

Use for:

- `setup-harness-skills`
- `session-start`
- `context-handover`
- `harness-issues`

Assertions should be deterministic Python checks:

- required files exist
- JSON parses successfully
- required fields are present
- old paths are absent
- state transitions are correct
- PLAN.md task blocks match required sections

### Layer 3: Fake External-System Evals

Add a fake `gh` executable or command recorder in the temp workspace. Skills and scripts can "call" `gh`, but the fake records calls to a JSON log instead of touching GitHub.

The provider returns:

```json
{
  "gh_calls": [
    {
      "argv": ["gh", "issue", "view", "42", "--json", "body,comments,labels"],
      "stdout": "{...}"
    },
    {
      "argv": ["gh", "api", "graphql"],
      "stdin_or_query": "mutation updateProjectV2ItemFieldValue ..."
    }
  ]
}
```

Use for:

- `setup-harness-skills`
- `harness-triage`
- `harness-issues`
- `context-handover` when posting progress comments

Assertions:

- issue body is read before labels are changed
- agent brief is posted before board field sync
- blocker issues are created before dependent issues
- `project_fields` absence skips GraphQL board mutations
- Effort maps to Size consistently
- mutation failures are non-blocking and reported

## Skill Coverage Matrix

| Skill | Eval type | Must prove |
|---|---|---|
| `harness-audit` | Text contract | Correct gaps, ordering, snippets, platform-specific guidance |
| `harness-guide` | Text contract | Three buckets, one next step, named anti-patterns |
| `setup-harness-skills` | Artifact + fake `gh` | Idempotent config writes, labels, board fields, project_fields capture |
| `session-start` | Artifact | Reads `.harness/state.json`, emits correct briefing, detects interrupted sessions |
| `context-handover` | Artifact + fake `gh` | Writes `.continue-here.json`, sets session idle, posts optional handover comment |
| `harness-triage` | Fake `gh` + text | Reads issue, applies state machine, posts disclaimer, syncs board fields |
| `harness-prd` | Text + artifact | Writes/mentions correct CONTEXT.md path, preserves WHAT/HOW separation |
| `harness-issues` | Artifact + fake `gh` | Creates vertical slice issues, writes PLAN.md, syncs board fields |
| `write-harness-skill` | Text contract | Asks requirements first, produces valid skill structure |
| `skill-cleanup` | Artifact | Detects stale installs, never removes without explicit confirmation |

## Provider Design

Keep the current provider for text-only evals:

- `provider.py`

Add two new providers:

- `provider_artifact.py`
- `provider_gh_fake.py`

### `provider_artifact.py`

Responsibilities:

1. Build a temp workspace from structured fixtures.
2. Inject SKILL.md and references as the system prompt.
3. Include a file tree and selected file contents in the user prompt.
4. Ask the model to produce either normal user-facing output or an explicit artifact plan.
5. Apply artifact writes only when the response contains a fenced `artifact-json` block.
6. Return output plus `files_before`, `files_after`, `changed_files`, and parse errors.

The explicit artifact block avoids pretending the model has real filesystem tools inside promptfoo. For example:

```json
{
  "writes": [
    {
      "path": ".harness/state.json",
      "content": "{\"version\":\"1.0\",\"session\":{\"status\":\"idle\"}}"
    }
  ]
}
```

The provider applies those writes to the temp workspace, then deterministic assertions inspect the result.

### `provider_gh_fake.py`

Responsibilities:

1. Build a temp workspace from fixtures.
2. Place a fake `gh` executable first on PATH.
3. Seed fake GitHub state from test vars:
   - issues
   - labels
   - comments
   - project fields
   - project items
4. Capture every fake `gh` call to `.eval/gh-calls.json`.
5. Return fake GitHub final state plus call log.

If direct subprocess execution is not possible in the promptfoo provider path, the fallback is an explicit `gh_calls` artifact block. The first implementation may use the artifact-block approach; the fake executable can come later.

## Fixture Design

Move away from plain-English scaffold hints for stateful tests. Use structured fixtures:

```yaml
vars:
  fixture:
    files:
      ".harness/state.json":
        json:
          version: "1.0"
          session:
            status: "in_progress"
            started_at: "2026-05-29T01:00:00Z"
            last_active: "2026-05-29T01:05:00Z"
          position:
            phase: "03-execute"
            active_task: "#42 - Add auth middleware"
            resume_file: ".harness/phases/03-execute/.continue-here.json"
      ".claude/harness.json":
        json:
          github:
            owner: "my-org"
            repo: "my-repo"
            project_v2_id: "PVT_123"
          project_fields:
            effort:
              id: "PVTF_effort"
            size:
              id: "PVTSSF_size"
              options:
                XS: "opt_xs"
                S: "opt_s"
                M: "opt_m"
                L: "opt_l"
                XL: "opt_xl"
```

Keep `scaffold_files` for legacy text evals until all configs migrate.

## Deterministic Assertions

Add reusable Python assertion helpers under `evals/promptfoo/assertions/`:

- `json_path_equals(output, file, path, expected)`
- `json_has_keys(output, file, keys)`
- `file_exists(output, path)`
- `file_not_exists(output, path)`
- `gh_call_sequence(output, patterns)`
- `no_stale_paths(output, forbidden_paths)`
- `effort_size_mapping(output)`
- `issue_template_valid(output)`
- `plan_md_valid(output)`

Promptfoo config can call these helpers from `type: python` assertions.

## Required Regression Guards

These guards should apply broadly:

- No eval fixture should use `.harness/STATE.md` unless explicitly testing migration.
- No primary handoff fixture should use `.continue-here.md`; current schema is `.continue-here.json`.
- No skill should write `.claude/session.json` as the primary session state.
- No issue creation eval may pass if any issue lacks an AC Source column.
- No board sync eval may pass if Effort 3 maps to anything other than Size M.
- No external-system eval may pass if it requires live GitHub.

## Initial Eval Backlog

### 1. `session-start` Schema Alignment

Replace stale fixtures with `.harness/state.json`.

Test cases:

- clean resume from idle state
- interrupted recovery from stale `in_progress`
- cold start with no state
- phase revert when execute lacks PLAN.md
- phase advance when PLAN.md exists

### 2. `context-handover` Artifact Proof

Test cases:

- execute phase writes `.continue-here.json`
- no state file still creates fallback state and resume file
- memory content is referenced by path, not inlined
- GitHub comment is skipped when tracker config is absent
- GitHub comment is posted when active task has issue number

### 3. `setup-harness-skills` Idempotency

Test cases:

- creates `.harness/config.json`, `.harness/state.json`, settings, and docs/agents seeds
- merges harness namespace into existing GSD config
- skips existing CI workflows
- writes `project_fields` after board metadata is available
- does not overwrite existing `project_fields`

### 4. `harness-triage` Fake GitHub

Test cases:

- attention view buckets unlabeled, needs-triage, needs-info with reporter activity
- quick override confirms mechanical steps before mutation
- ready-for-agent posts agent brief with disclaimer
- board sync guard skips when `project_fields` absent
- Effort 3 syncs Size M and asks Priority once

### 5. `harness-issues` Fake GitHub + PLAN.md

Test cases:

- vague feature fails creation gates
- approved breakdown creates issues in dependency order
- each issue has Story, Confidence, AC table, DoD, Effort, Dependencies
- writes `.harness/phases/02-plan/02-PLAN.md`
- board field sync runs once per created issue

### 6. `skill-cleanup` Coverage

Create `evals/promptfoo/skill-cleanup.yaml`.

Test cases:

- stale renamed skill is detected
- orphaned platform copy is detected
- dry-run does not remove files
- removal plan asks for explicit confirmation
- platform entries are removed before central store in the proposed sequence

## Rollout Plan

### Phase 1: Schema Repair

- Update stale `session-start` promptfoo fixtures.
- Add regression assertions banning stale paths.
- Keep provider architecture unchanged.

### Phase 2: Artifact Provider

- Add `provider_artifact.py`.
- Add structured fixture support.
- Convert `context-handover` and `session-start` first.

### Phase 3: Fake GitHub Provider

- Add fake GitHub state fixture format.
- Add `gh_calls` capture.
- Convert board sync tests for `harness-triage` and `harness-issues`.

### Phase 4: Coverage Completion

- Add `skill-cleanup` eval config.
- Add missing setup idempotency assertions.
- Convert weak rubrics to deterministic Python where possible.

### Phase 5: CI Gate

- Update `evals/run_evals.py` to support:
  - `--tier text`
  - `--tier artifact`
  - `--tier external`
  - `--skill NAME`
- Keep default local run to text + artifact.
- Make fake GitHub tests part of CI once stable.

## Acceptance Criteria

- `python evals/run_evals.py --skill session-start` no longer references `.harness/STATE.md`.
- `context-handover` eval fails if `.continue-here.json` is missing or invalid JSON.
- `harness-issues` eval fails if PLAN.md is not written.
- `harness-triage` eval fails if board sync happens before the agent brief is posted.
- `setup-harness-skills` eval fails if existing `project_fields` are overwritten.
- `skill-cleanup` has a promptfoo config and at least five cases.
- At least one deterministic Python assertion exists for every non-advisory skill.
- No eval requires live GitHub access.

## Risks

### Risk: The provider becomes a second implementation of the skills

Mitigation: the provider should only apply explicit artifact blocks and inspect outcomes. It should not decide what files should be written.

### Risk: Artifact blocks make tests less realistic

Mitigation: use them as an intermediate step. The long-term direction is fake tool execution or trajectory capture, but artifact blocks immediately close the "prose only" gap.

### Risk: More deterministic tests make model variance painful

Mitigation: keep text-heavy skills on rubrics and use deterministic checks only where the outcome is objectively structured.

### Risk: Multi-turn skills still cannot be fully tested

Mitigation: split multi-turn flows into first-response tests, approved-state artifact tests, and fake external mutation tests. Full conversation simulation is optional later work.

## Open Questions

1. Should artifact blocks be visible in normal model output, or should provider prompts ask for a hidden machine-readable trailer?
2. Should fake GitHub state emulate `gh` command output exactly, or use a simpler domain-specific command log first?
3. Should CI run all tiers by default, or keep external/fake-GitHub tests opt-in until stable?
