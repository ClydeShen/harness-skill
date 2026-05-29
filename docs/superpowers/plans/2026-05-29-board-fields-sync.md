# Board Fields Sync Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up Priority, Size, and Effort board-field population across `setup-harness-skills` (issue #11), `harness-triage` (issue #12), and `harness-issues` (issue #13) per the approved spec at `docs/superpowers/specs/2026-05-29-board-fields-sync-design.md`.

**Architecture:** All three issues change markdown skill files only — no executable code. The test mechanism is promptfoo eval scenarios (LLM-judge assertions). Each issue follows the same TDD pattern: write failing eval scenarios first, run to confirm failure, add skill content, run again to confirm pass. Issues are implemented in dependency order (#11 before #12 and #13).

**Tech Stack:** Markdown skill files, promptfoo YAML eval configs, llamacpp HTTP at `localhost:8080` (grader + provider).

---

## Chunk 1: Issue #11 — setup-harness-skills project_fields population

**Files modified:**
- `evals/promptfoo/setup-harness-skills.yaml` — add evals #7 and #8
- `skills/engineering/setup-harness-skills/output-steps.md` — expand Step 5 with field creation, GraphQL query, project_fields write
- `skills/engineering/setup-harness-skills/SKILL.md` — add `project_fields` to the harness.json documentation
- `skills/engineering/setup-harness-skills/github-project.md` — add Priority row to Custom fields table

### Task 1: Write failing evals for issue #11

**Files:**
- Modify: `evals/promptfoo/setup-harness-skills.yaml`

- [ ] **Step 1: Add eval #7 (project_fields written) to setup-harness-skills.yaml**

Append after the last test block (after eval #6):

```yaml
  # ---------------------------------------------------------------------------
  # Eval 7: project_fields written to harness.json after board creation
  # ---------------------------------------------------------------------------
  - description: "#7 project_fields written — Step 5 queries board metadata and writes project_fields"
    vars:
      prompt: "/setup-harness-skills"
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - ".claude/harness.json with project_v2_id set to PVT_abc123"
    assert:
      - type: llm-rubric
        value: After creating the board, queries board field metadata using gh api graphql to retrieve field IDs for Priority, Size, and Effort (windows)
      - type: llm-rubric
        value: Writes project_fields key to .claude/harness.json containing priority.id, priority.options, size.id, size.options, and effort.id
      - type: llm-rubric
        value: Creates Priority single-select field (P1/P2/P3) and Size single-select field (XS/S/M/L/XL) on the board if they do not already exist

  # ---------------------------------------------------------------------------
  # Eval 8: project_fields idempotent — merge over existing values, never overwrite
  # ---------------------------------------------------------------------------
  - description: "#8 project_fields idempotent — re-run merges, never overwrites existing keys"
    vars:
      prompt: "/setup-harness-skills"
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - ".claude/harness.json with project_fields.priority already populated"
    assert:
      - type: llm-rubric
        value: When project_fields already contains populated keys, the skill merges over existing values and does NOT overwrite keys that are already present
      - type: llm-rubric
        value: Describes the project_fields write as idempotent or states it skips keys already present
```

- [ ] **Step 2: Run evals to confirm #7 and #8 fail (skill doesn't yet have the content)**

```
python evals/run_evals.py --skill setup-harness-skills --filter "#7|#8"
```

Expected: both evals fail — skill output won't mention project_fields or GraphQL query.

- [ ] **Step 3: Expand Step 5 in output-steps.md**

Replace the current Step 5 content:

```markdown
## Step 5 — Create GitHub Project v2 board

Only if user opted in during Section D:
- Create board via `gh project create`
- Add `Effort (windows)` number field
- Write `project_v2_id` and `project_board_name` back to `harness.json`
```

With the full expanded version including field creation, GraphQL query, and project_fields write (see exact content in Task 1, Step 3 body below).

**Exact replacement for Step 5:**

```markdown
## Step 5 — Create GitHub Project v2 board

Only if user opted in during Section D:

1. Create board and add `Effort (windows)` number field:
   ```bash
   PROJECT_NUMBER=$(gh project create --owner "$OWNER" --title "$BOARD_NAME" --format json --jq '.number')
   gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
     --name "Effort (windows)" --data-type "NUMBER"
   ```

2. Create `Priority` and `Size` single-select fields if not already present (idempotent — check existing fields first):
   ```bash
   # Check existing fields before creating
   EXISTING=$(gh project field-list $PROJECT_NUMBER --owner "$OWNER" --format json --jq '[.fields[].name]')

   # Create Priority if absent
   echo "$EXISTING" | grep -q '"Priority"' || \
     gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
       --name "Priority" --data-type "SINGLE_SELECT" \
       --single-select-options "P1,P2,P3"

   # Create Size if absent
   echo "$EXISTING" | grep -q '"Size"' || \
     gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
       --name "Size" --data-type "SINGLE_SELECT" \
       --single-select-options "XS,S,M,L,XL"
   ```

3. Query field metadata to capture IDs and option maps:
   ```bash
   PROJECT_ID=$(gh project view $PROJECT_NUMBER --owner "$OWNER" --format json --jq '.id')

   gh api graphql -f query='
   query($board: ID!) {
     node(id: $board) {
       ... on ProjectV2 {
         fields(first: 20) {
           nodes {
             ... on ProjectV2SingleSelectField { id name options { id name } }
             ... on ProjectV2Field { id name dataType }
           }
         }
       }
     }
   }' -f board="$PROJECT_ID"
   ```

   Map results:
   - Field named `Priority` → `project_fields.priority` (`id` + `options` map `{P1: <id>, P2: <id>, P3: <id>}`)
   - Field named `Size` → `project_fields.size` (`id` + `options` map `{XS: <id>, S: <id>, M: <id>, L: <id>, XL: <id>}`)
   - Field named `Effort (windows)` → `project_fields.effort` (`id` only)
   - Skip any field not found (partial population is valid).

4. Merge `project_fields` key into `.claude/harness.json` (idempotent — merge over existing values; never overwrite keys already present):
   ```json
   {
     "project_fields": {
       "priority": {
         "id": "<PVTSSF_... from board>",
         "options": { "P1": "<option-id>", "P2": "<option-id>", "P3": "<option-id>" }
       },
       "size": {
         "id": "<PVTSSF_... from board>",
         "options": {
           "XS": "<option-id>",
           "S":  "<option-id>",
           "M":  "<option-id>",
           "L":  "<option-id>",
           "XL": "<option-id>"
         }
       },
       "effort": {
         "id": "<PVTF_... from board>"
       }
     }
   }
   ```

5. Write `project_v2_id`, `project_board_name`, and `project_number` back to `harness.json`.

**Graceful degradation:** If the board has no Priority/Size/Effort (windows) fields, omit the corresponding sub-key. Downstream skills check for key presence before calling mutations.
```

- [ ] **Step 4: Add project_fields to SKILL.md harness.json documentation**

In SKILL.md, after the `.harness/ files written by setup-harness-skills` section, find where `.claude/harness.json` is described (the schema shown in Step 2 of output-steps.md) and add a note that Step 5 also appends `project_fields`. The Output section ends with "Run `/session-start` to begin your first session." — add the note just before that line.

Exact insertion after the Migration section in SKILL.md (after the `Old files are NOT deleted — user confirms before removal` line):

```markdown
### .claude/harness.json — project_fields (written by Step 5)

When a GitHub Project v2 board is configured, Step 5 appends a `project_fields` key with field IDs and option maps. Downstream skills (`harness-triage`, `harness-issues`) read this key before syncing board fields. If absent, those skills skip board sync and print a warning.
```

- [ ] **Step 5: Add Priority row to github-project.md Custom fields table**

Replace the existing Custom fields table:

```markdown
| Field | Type | Unit | Mapping |
|---|---|---|---|
| **Effort (windows)** | number | Token budget | 1 = ~150K–200K tokens (single slice); 2 = ~300K–400K (1 phase); 3 = ~500K–700K (full feature); 4+ = epic |
| **Size** | T-shirt | Rough relative | XS ≤ 1 window; S = 2; M = 3–4; L = 5–6; XL ≥ 7 |
```

With:

```markdown
| Field | Type | Unit | Mapping |
|---|---|---|---|
| **Effort (windows)** | number | Token budget | 1 = ~150K–200K tokens (single slice); 2 = ~300K–400K (1 phase); 3 = ~500K–700K (full feature); 4+ = epic |
| **Size** | T-shirt | Rough relative | XS ≤ 1 window; S = 2; M = 3–4; L = 5–6; XL ≥ 7 |
| **Priority** | single-select | Urgency tier | P1 = critical/blocking; P2 = normal; P3 = low/nice-to-have |
```

Add a note below the table:

```markdown
All three fields are created and populated automatically by harness skills: `setup-harness-skills` creates them on the board and writes their IDs to `.claude/harness.json`; `harness-triage` and `harness-issues` set the values per issue.
```

- [ ] **Step 6: Run evals to confirm #7 and #8 pass**

```
python evals/run_evals.py --skill setup-harness-skills --filter "#7|#8"
```

Expected: both evals pass. Also run the full suite to check for regressions:

```
python evals/run_evals.py --skill setup-harness-skills
```

Expected: all 8 evals pass.

- [ ] **Step 7: Commit issue #11**

```bash
git add evals/promptfoo/setup-harness-skills.yaml \
        skills/engineering/setup-harness-skills/output-steps.md \
        skills/engineering/setup-harness-skills/SKILL.md \
        skills/engineering/setup-harness-skills/github-project.md
git commit -m "feat(setup-harness-skills): Step 5 queries board fields and writes project_fields to harness.json"
```

---

## Chunk 2: Issue #12 — harness-triage board field sync

**Files modified:**
- `evals/promptfoo/harness-triage.yaml` — add evals #6 and #7
- `skills/engineering/harness-triage/SKILL.md` — add board field sync step after agent brief posted

### Task 2: Write failing evals and implement harness-triage sync

**Files:**
- Modify: `evals/promptfoo/harness-triage.yaml`
- Modify: `skills/engineering/harness-triage/SKILL.md`

- [ ] **Step 1: Add eval #6 (board sync after brief) and #7 (guard) to harness-triage.yaml**

Append after the last test block (after eval #5):

```yaml
  # ---------------------------------------------------------------------------
  # Eval 6: board field sync after agent brief posted
  # ---------------------------------------------------------------------------
  - description: "#6 board field sync — syncs Effort, Size, Priority after agent brief posted"
    vars:
      prompt: >
        /harness-triage #42
        The issue is ready. Post an agent brief with Effort: 3, then sync the board fields.
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - ".claude/harness.json with project_fields populated (priority.id, size.id, effort.id)"
    assert:
      - type: llm-rubric
        value: After the agent brief is posted, reads project_fields from .claude/harness.json
      - type: llm-rubric
        value: Derives Size from Effort using the mapping — Effort 3 maps to Size M (3-4 windows = M)
      - type: llm-rubric
        value: Asks the maintainer for Priority (P1 / P2 / P3 / skip) exactly once after the brief is confirmed
      - type: llm-rubric
        value: Prints a confirmation line containing Effort, Size, and Priority (or "not set") after board field mutations

  # ---------------------------------------------------------------------------
  # Eval 7: board sync guard — skips with warning if project_fields absent
  # ---------------------------------------------------------------------------
  - description: "#7 board sync guard — skips sync when project_fields absent from harness.json"
    vars:
      prompt: >
        /harness-triage #42
        Move to ready-for-agent and post an agent brief.
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - ".claude/harness.json WITHOUT project_fields key"
    assert:
      - type: llm-rubric
        value: When project_fields is absent from harness.json, prints a warning containing "project_fields not in harness.json" and mentions running /setup-harness-skills
      - type: llm-rubric
        value: Skips board field mutations entirely — does not attempt GraphQL calls when project_fields is absent
      - type: llm-rubric
        value: Does NOT block the triage outcome — the issue brief is still posted even when board sync is skipped
```

- [ ] **Step 2: Run evals to confirm #6 and #7 fail**

```
python evals/run_evals.py --skill harness-triage --filter "#6|#7"
```

Expected: both fail — SKILL.md has no board sync section.

- [ ] **Step 3: Add board field sync section to harness-triage SKILL.md**

Insert a new section `## Board field sync` after the `## Triage a specific issue` section (after step 5 "Apply the outcome" bullets end, before `## Quick state override`):

```markdown
## Board field sync

**Trigger:** After the maintainer confirms `ready-for-agent` or `ready-for-human` AND the agent brief comment is posted.

**Guard:** Read `.claude/harness.json` → `project_fields`. If absent or empty:
```
⚠️ project_fields not in harness.json — skipping board field sync. Run /setup-harness-skills to populate.
```
Do not block the triage outcome — continue even if sync is skipped.

**Effort-to-Size mapping:**

| Effort (windows) | Size |
|---|---|
| 1 | XS |
| 2 | S |
| 3–4 | M |
| 5–6 | L |
| 7+ | XL |

**Sequence:**

1. Read `github.project_v2_id` from `.claude/harness.json` — this is the `projectId` for all mutations.
2. Query `repository.issue.projectItems` to get the board item ID. If the issue is not yet on the board, call `addProjectV2ItemByContentId(projectId, contentId: issueNodeId)` to add it and capture the new item ID.
3. Parse Effort integer from the agent brief text (`**Effort:** N` line).
4. Derive Size from Effort using the mapping above.
5. Ask maintainer for Priority — one question, after brief is confirmed: `"Priority? P1 / P2 / P3 / skip"` — default skip.
6. Call `updateProjectV2ItemFieldValue` for Effort (number), Size (singleSelectOptionId), and Priority (if not skipped).
7. Print confirmation: `✅ Board fields updated — Effort: N, Size: X, Priority: Pn` (or `Priority: not set`).

**Error handling:** If any mutation fails (e.g. token lacks project scope), print `⚠️ Board field update failed: <error>` and continue — do not block the triage outcome.
```

- [ ] **Step 4: Run evals to confirm #6 and #7 pass**

```
python evals/run_evals.py --skill harness-triage --filter "#6|#7"
```

Expected: both pass. Run full suite:

```
python evals/run_evals.py --skill harness-triage
```

Expected: all 7 evals pass.

- [ ] **Step 5: Commit issue #12**

```bash
git add evals/promptfoo/harness-triage.yaml \
        skills/engineering/harness-triage/SKILL.md
git commit -m "feat(harness-triage): sync Effort, Size, Priority to board after agent brief posted"
```

---

## Chunk 3: Issue #13 — harness-issues board field sync

**Files modified:**
- `evals/promptfoo/harness-issues.yaml` — add evals #6 and #7
- `skills/engineering/harness-issues/SKILL.md` — add board field sync step per issue after creation

### Task 3: Write failing evals and implement harness-issues sync

**Files:**
- Modify: `evals/promptfoo/harness-issues.yaml`
- Modify: `skills/engineering/harness-issues/SKILL.md`

- [ ] **Step 1: Add eval #6 (board sync per issue) and #7 (guard) to harness-issues.yaml**

Append after the last test block (after eval #5):

```yaml
  # ---------------------------------------------------------------------------
  # Eval 6: board field sync per issue — Effort, Size, Priority set after each creation
  # ---------------------------------------------------------------------------
  - description: "#6 board field sync per issue — syncs fields after each issue is created"
    vars:
      prompt: >
        /harness-issues
        Break down the CSV export feature into issues and sync board fields.
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - "docs/prd.md with CSV export spec including Effort estimates and priority:p2 labels"
        - ".claude/harness.json with project_fields populated"
    assert:
      - type: llm-rubric
        value: After each issue is created, fetches the issue node ID and adds it to the project board
      - type: llm-rubric
        value: Parses Effort from the issue body (Estimate line) and derives Size using the XS/S/M/L/XL mapping
      - type: llm-rubric
        value: Maps priority:p2 label to board Priority field value P2; prints per-issue confirmation with Effort, Size, and Priority

  # ---------------------------------------------------------------------------
  # Eval 7: board sync guard — skips with warning if project_fields absent
  # ---------------------------------------------------------------------------
  - description: "#7 board sync guard — skips per-issue sync when project_fields absent"
    vars:
      prompt: >
        /harness-issues
        Create issues for the search feature.
      scaffold_files:
        - "package.json"
        - "CLAUDE.md"
        - "docs/prd.md with search feature spec"
        - ".claude/harness.json WITHOUT project_fields key"
    assert:
      - type: llm-rubric
        value: When project_fields is absent from harness.json, prints a warning containing "project_fields not in harness.json" and mentions running /setup-harness-skills
      - type: llm-rubric
        value: Issue creation itself is NOT blocked — issues are still created on GitHub even when board sync is skipped
```

- [ ] **Step 2: Run evals to confirm #6 and #7 fail**

```
python evals/run_evals.py --skill harness-issues --filter "#6|#7"
```

Expected: both fail.

- [ ] **Step 3: Add board field sync to harness-issues SKILL.md**

In the `### 5. Publish the issues to the issue tracker` section, expand the per-issue publish process. The current text is:

> For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. These issues are considered ready for AFK agents, so publish them with the correct triage label unless instructed otherwise.
>
> Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

After this paragraph (before the `<issue-template>` block), insert the board sync instructions as a new subsection. The instructions describe what happens AFTER each issue is created and AFTER the `<issue-template>` block, so insert at the end of section 5, after the `<issue-template>` closing tag. Add:

```markdown
#### Per-issue board field sync

After each issue is created, sync its fields to the project board:

**Guard:** Read `.claude/harness.json` → `project_fields`. If absent:
```
⚠️ project_fields not in harness.json — skipping board field sync. Run /setup-harness-skills to populate.
```
Issue creation is NOT blocked — continue even if sync is skipped.

**Effort-to-Size mapping:**

| Effort (windows) | Size |
|---|---|
| 1 | XS |
| 2 | S |
| 3–4 | M |
| 5–6 | L |
| 7+ | XL |

**Sequence per issue:**

1. Read `github.project_v2_id` from `.claude/harness.json` — this is the `projectId` for all mutations.
2. Capture the issue number from `gh issue create` output.
3. Fetch issue node ID: `gh issue view N --json id --jq '.id'`.
4. Add to project board: `addProjectV2ItemByContentId(projectId, contentId: nodeId)` → capture item ID.
5. Parse Effort integer from the issue body (`Estimate: **N context window(s)**` line).
6. Derive Size from Effort using the mapping above.
7. Resolve Priority from labels: `priority:p1 → P1`, `priority:p2 → P2`, `priority:p3 → P3`; skip if no priority label present.
8. Call `updateProjectV2ItemFieldValue` for Effort (number) and Size (singleSelectOptionId); call for Priority if resolved.
9. Print per-issue confirmation: `✅ #N board fields — Effort: N, Size: X, Priority: Pn / not set`.

**Error handling:** Mutation failure is non-blocking — print `⚠️ Board field update failed for #N: <error>` and continue to the next issue.
```

- [ ] **Step 4: Run evals to confirm #6 and #7 pass**

```
python evals/run_evals.py --skill harness-issues --filter "#6|#7"
```

Expected: both pass. Run full suite:

```
python evals/run_evals.py --skill harness-issues
```

Expected: all 7 evals pass.

- [ ] **Step 5: Commit issue #13**

```bash
git add evals/promptfoo/harness-issues.yaml \
        skills/engineering/harness-issues/SKILL.md
git commit -m "feat(harness-issues): sync Effort, Size, Priority to board after each issue created"
```

---

## Final: Close issues on GitHub

- [ ] Close issue #11 with comment "Implemented in [commit hash]"
- [ ] Close issue #12 with comment "Implemented in [commit hash]"
- [ ] Close issue #13 with comment "Implemented in [commit hash]"
- [ ] Update `.harness/phases/03-execute/.continue-here.json` — mark all three issues complete

---

*Spec: `docs/superpowers/specs/2026-05-29-board-fields-sync-design.md`*
*Blocker (user action): recreate `GH_PROJECT_TOKEN` as classic PAT with `repo + project` scopes before board mutations work at runtime.*
