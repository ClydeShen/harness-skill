# Setup Harness GitHub Templates Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix `setup-harness-skills` so it generates harness-format issue templates and uses an idempotent, minimal CI scaffold instead of a broken stack-detecting one.

**Architecture:** Three targeted edits — rewrite Step 7 in `output-steps.md`, insert new Step 7a, create two source template files in `github-issue-templates/`. TDD order: add eval assertions first, then implement, then verify evals pass.

**Tech Stack:** Markdown, YAML (promptfoo), bash eval runner

**Spec:** `docs/superpowers/specs/2026-05-29-setup-harness-github-templates-design.md`

---

## Chunk 1: Eval scenarios (failing tests)

### Task 1: Add eval scenarios for new behaviors

**Files:**
- Modify: `evals/promptfoo/setup-harness-skills.yaml`

These evals will fail until the `output-steps.md` changes are made — that's the point.

- [ ] **Step 1: Append Eval 5 — CI idempotency guard**

  Add to `evals/promptfoo/setup-harness-skills.yaml` after the existing tests block:

  ```yaml
    # ---------------------------------------------------------------------------
    # Eval 5: CI idempotency — existing workflows detected, Step 7 skipped
    # ---------------------------------------------------------------------------
    - description: "#5 CI idempotency — skips Step 7 when workflows exist"
      vars:
        prompt: "/setup-harness-skills"
        scaffold_files:
          - "package.json"
          - "CLAUDE.md"
          - ".github/workflows/test.yml with existing workflow"
      assert:
        - type: llm-rubric
          value: Detects existing .github/workflows/*.yml file during the explore step
        - type: llm-rubric
          value: Skips CI scaffold (Step 7) and records "CI scaffold skipped — existing workflows found" in the setup summary
        - type: llm-rubric
          value: Does NOT overwrite or modify the existing workflow file

    # ---------------------------------------------------------------------------
    # Eval 6: Issue templates written — Step 7a
    # ---------------------------------------------------------------------------
    - description: "#6 issue templates — Step 7a writes harness-issue.md and bug-report.md"
      vars:
        prompt: "/setup-harness-skills"
        scaffold_files:
          - "package.json"
          - "CLAUDE.md"
      assert:
        - type: llm-rubric
          value: Writes .github/ISSUE_TEMPLATE/harness-issue.md with Story / Confidence / Acceptance Criteria / Definition of Done / Effort / Dependencies sections
        - type: llm-rubric
          value: Writes .github/ISSUE_TEMPLATE/bug-report.md with What's broken / Steps to reproduce / Expected behavior / Acceptance Criteria / Definition of Done sections
        - type: llm-rubric
          value: Records "✅ .github/ISSUE_TEMPLATE/harness-issue.md written" and "✅ .github/ISSUE_TEMPLATE/bug-report.md written" in the setup summary
        - type: llm-rubric
          value: Step 7a is idempotent — skips any file that already exists at the destination
  ```

- [ ] **Step 2: Commit the failing evals**

  ```bash
  git add evals/promptfoo/setup-harness-skills.yaml
  git commit -m "test(evals): add failing eval scenarios #5 and #6 for CI idempotency and issue templates"
  ```

---

## Chunk 2: Implementation

### Task 2: Rewrite Step 7 in output-steps.md (CI idempotency)

**Files:**
- Modify: `skills/engineering/setup-harness-skills/output-steps.md`

The current Step 7 does stack-detection with no idempotency guard. Replace its body entirely.

- [ ] **Step 3: Replace Step 7 body**

  Find the existing Step 7 section:
  ```
  ## Step 7 — Scaffold `.github/workflows/ci.yml`

  Stack-specific based on files detected in Step 1:
  - Node.js (`package.json` present): Node CI template
  - Python (`requirements.txt` / `pyproject.toml`): Python CI template
  - Unknown stack: minimal placeholder CI
  ```

  Replace with:
  ```markdown
  ## Step 7 — Scaffold `.github/workflows/ci.yml`

  **Idempotency guard:** Before writing, check for any `*.yml` in `.github/workflows/`. If any exist, skip this step and record in the setup summary:

  ```
  ⚠️ CI scaffold skipped — existing workflows found
  ```

  **When no workflows exist:** Write a minimal stack-agnostic placeholder:

  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        # TODO: add your build/test steps here
  ```

  Record in the setup summary: `✅ .github/workflows/ci.yml written (placeholder — customize for your stack)`
  ```

  > Note: the outer code fences in the yaml block will be ``` yaml (no space) in the actual file.

- [ ] **Step 4: Insert Step 7a immediately after Step 7**

  Add the following section directly after the Step 7 block (before `## Step 8`):

  ```markdown
  ## Step 7a — Write harness issue templates to `.github/ISSUE_TEMPLATE/`

  Copy from this skill's `github-issue-templates/` folder to `.github/ISSUE_TEMPLATE/` in the target project.

  Idempotent: skip any file that already exists at the destination.

  Files to copy:
  - `github-issue-templates/harness-issue.md` → `.github/ISSUE_TEMPLATE/harness-issue.md`
  - `github-issue-templates/bug-report.md` → `.github/ISSUE_TEMPLATE/bug-report.md`

  Record in the setup summary:
  ```
  ✅ .github/ISSUE_TEMPLATE/harness-issue.md written
  ✅ .github/ISSUE_TEMPLATE/bug-report.md written
  ```
  ```

- [ ] **Step 5: Commit the output-steps edit**

  ```bash
  git add skills/engineering/setup-harness-skills/output-steps.md
  git commit -m "fix(setup-harness-skills): Step 7 idempotency guard + minimal CI placeholder; insert Step 7a issue templates"
  ```

---

### Task 3: Create issue template source files

**Files:**
- Create: `skills/engineering/setup-harness-skills/github-issue-templates/harness-issue.md`
- Create: `skills/engineering/setup-harness-skills/github-issue-templates/bug-report.md`

- [ ] **Step 6: Create `github-issue-templates/harness-issue.md`**

  Content (exact, from spec):

  ```markdown
  ---
  name: Harness Issue
  about: Feature, task, chore, or spike — follows the harness AC template
  title: '[type]: '
  labels: 'status:triage'
  ---
  ## Story
  As a [role], I want [capability], so that [benefit].

  ## Confidence: AFK ✓ / HITL ⚠
  > Agent confidence: **AFK** — all sources cited below.
  > (or: **HITL** — missing: [specific gap description])

  ## Acceptance Criteria
  | # | Criterion | Type | Source |
  |---|---|---|---|
  | 1 | Given X, when Y, then Z | happy path | Spec §N.N |
  | 2 | Given X, when error, then W | sad path | User statement YYYY-MM-DD |

  ## Definition of Done
  - [ ] All AC pass (verified by agent or CI)
  - [ ] PR merged to main
  - [ ] No regressions in related tests
  - [ ] Implementation notes written if agent deviated from spec

  ## Effort
  Estimate: **N context window(s)**

  ## Dependencies
  Blocked by: #NNN / None
  ```

- [ ] **Step 7: Create `github-issue-templates/bug-report.md`**

  Content (exact, from spec):

  ```markdown
  ---
  name: Bug Report
  about: Something is broken — follows the harness AC template
  title: 'bug: '
  labels: 'status:triage,type:bug'
  ---
  ## What's broken
  [Describe the observed behavior and where it occurs]

  ## Steps to reproduce
  1.
  2.
  3.

  ## Expected behavior
  [What should happen instead]

  ## Acceptance Criteria
  | # | Criterion | Type | Source |
  |---|---|---|---|
  | 1 | Given X, when Y, then Z | happy path | Reproduction steps |

  ## Definition of Done
  - [ ] All AC pass
  - [ ] PR merged to main
  - [ ] No regressions

  ## Effort
  Estimate: **N context window(s)**

  ## Optional
  - **Environment:** [OS, browser, version, etc.]
  - **Logs / screenshots:** [paste or attach]
  - **Workaround known:** yes / no
  ```

- [ ] **Step 8: Commit the new source files**

  ```bash
  git add skills/engineering/setup-harness-skills/github-issue-templates/
  git commit -m "feat(setup-harness-skills): add harness-issue and bug-report source templates for Step 7a"
  ```

---

## Chunk 3: Verify

### Task 4: Run evals and verify

- [ ] **Step 9: Run setup-harness-skills evals**

  ```bash
  python evals/run_evals.py --skill setup-harness-skills
  ```

  Expected: all 6 scenarios pass (including the 2 new ones). If any fail, investigate — the likely cause is Step 7a wording not matching the eval rubric; adjust `output-steps.md` to match.

- [ ] **Step 10: Close issue #10 on GitHub**

  ```bash
  gh issue close 10 --comment "Implemented: Step 7 idempotency guard, Step 7a harness issue templates, source files in github-issue-templates/. Evals pass." --reason completed
  ```

- [ ] **Step 11: Update .continue-here.json to done**

  Set `.harness/phases/03-execute/.continue-here.json` `status` to `"done"` and clear `remaining_work`.
