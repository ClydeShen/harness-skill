# Design: Sync Priority, Size, and Effort to Project Board Fields

**Date:** 2026-05-29
**Status:** Approved

## Problem

When `harness-triage` posts an agent brief or `harness-issues` creates an issue, Priority, Size, and Effort are written only into the issue body text. The GitHub Projects v2 board fields (Priority single-select, Size single-select, Effort (windows) number) remain unpopulated — making board filtering and reporting useless for these dimensions.

## Solution Overview

Three targeted changes:

1. **`harness.json` schema extension** — add `project_fields` key with field IDs and option maps; `setup-harness-skills` Step 5 writes it automatically.
2. **`harness-triage` SKILL.md** — after agent brief is posted, sync Effort + Size from brief's Effort value; ask maintainer once for Priority.
3. **`harness-issues` SKILL.md** — after each issue is created and added to the board, sync Effort + Size from body Effort; set Priority from `priority:pN` label if present.

## Change 1 — `harness.json` schema extension

`setup-harness-skills` Step 5 (Create GitHub Project v2 board) gains one additional action: query the board's field metadata and write a `project_fields` key into `.claude/harness.json`.

### Schema

```json
{
  "github": { "...": "existing keys unchanged" },
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

### Board field creation

Step 5 must also ensure `Priority` (single-select: P1/P2/P3) and `Size` (single-select: XS/S/M/L/XL) fields exist on the board. `Effort (windows)` is already created in the existing Step 5 text. Add the two missing fields if not present:

```bash
gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
  --name "Priority" --data-type "SINGLE_SELECT" \
  --single-select-options "P1,P2,P3"

gh project field-create $PROJECT_NUMBER --owner "$OWNER" \
  --name "Size" --data-type "SINGLE_SELECT" \
  --single-select-options "XS,S,M,L,XL"
```

Skip creation if a field with that name already exists (idempotent).

### Setup query

After confirming/creating the fields, query field metadata to capture IDs:

```bash
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

Map results: field named `Priority` → `project_fields.priority`, `Size` → `project_fields.size`, `Effort (windows)` → `project_fields.effort`. Skip any field not found (partial population is valid).

**Idempotent:** merge over existing `project_fields` values; never overwrite keys already present.

**Graceful degradation:** if the board has no Priority/Size/Effort (windows) fields, omit the corresponding sub-key. Downstream skills check for key presence before calling mutations.

## Change 2 — `harness-triage` SKILL.md

### Trigger

After the maintainer confirms `ready-for-agent` or `ready-for-human` AND the agent brief comment is posted.

### Guard

Read `.claude/harness.json` → `project_fields`. If absent or empty:
```
⚠️ project_fields not in harness.json — skipping board field sync. Run /setup-harness-skills to populate.
```

### Fields set

| Field | Source | Logic |
|---|---|---|
| **Effort (windows)** | `**Effort:** N` line in agent brief | Extract integer N; call number mutation |
| **Size** | Derived from Effort | XS ≤ 1 / S = 2 / M = 3–4 / L = 5–6 / XL ≥ 7 |
| **Priority** | Maintainer input | Ask once after brief is confirmed: "Priority? P1 / P2 / P3 / skip" — default skip |

### Sequence

1. Read `github.project_v2_id` from `.claude/harness.json` — this is the `projectId` for all mutations.
2. Query `repository.issue.projectItems` to get the board item ID. Triage operates on existing issues, so the issue is usually already on the board — this query is expected to return a result in the common case. If the result is empty (issue was never added to the board), call `addProjectV2ItemByContentId(projectId, contentId: issueNodeId)` to add it and capture the new item ID.
3. Parse Effort integer from agent brief text.
4. Ask maintainer for Priority (one question, after brief posted).
5. Call `updateProjectV2ItemFieldValue` for Effort, Size, and Priority (if not skipped).
6. Print confirmation: `✅ Board fields updated — Effort: N, Size: X, Priority: Pn` (or `Priority: not set`).

### Error handling

If any mutation fails (e.g. token lacks project scope), print `⚠️ Board field update failed: <error>` and continue — do not block the triage outcome.

## Change 3 — `harness-issues` SKILL.md

### Trigger

After each issue is created via `gh issue create` (runs once per issue, not once per batch).

### Guard

Same as Change 2 — read `project_fields` from `harness.json`; skip with note if absent.

### Fields set

| Field | Source | Logic |
|---|---|---|
| **Effort (windows)** | `## Effort` section in issue body | Parse the line `Estimate: **N context window(s)**`; extract integer N |
| **Size** | Derived from Effort | XS ≤ 1 / S = 2 / M = 3–4 / L = 5–6 / XL ≥ 7 |
| **Priority** | `priority:pN` label on the issue | Map `priority:p1 → P1`, `priority:p2 → P2`, `priority:p3 → P3`; skip if no priority label |

### Sequence per issue

1. Read `github.project_v2_id` from `.claude/harness.json` — this is the `projectId` for all mutations.
2. Create issue with `gh issue create` → capture issue number.
3. Fetch issue node ID: `gh issue view N --json id --jq '.id'`.
4. Add to project board: `addProjectV2ItemByContentId(projectId, contentId: nodeId)` → capture item ID.
5. Parse Effort from body; derive Size.
6. Resolve Priority from labels (skip if none).
7. Call `updateProjectV2ItemFieldValue` for Effort and Size (always); Priority (if resolved).
8. Print per-issue confirmation: `✅ #N board fields — Effort: N, Size: X, Priority: Pn / not set`.

### Error handling

Same as Change 2 — mutation failure is non-blocking; print warning and continue to next issue.

## Effort-to-Size mapping (shared rule)

| Effort (windows) | Size |
|---|---|
| 1 | XS |
| 2 | S |
| 3–4 | M |
| 5–6 | L |
| 7+ | XL |

This mapping is defined once here. Both skills apply it identically.

## GraphQL mutation shapes (reference)

**Number field** (Effort):
```bash
gh api graphql -f query='
  mutation($project: ID!, $item: ID!, $field: ID!, $value: Float!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $project, itemId: $item, fieldId: $field,
      value: { number: $value }
    }) { projectV2Item { id } }
  }' \
  -f project="$PROJECT_ID" -f item="$ITEM_ID" \
  -f field="<effort.id>" -F value=2
```

**Single-select field** (Priority, Size):
```bash
gh api graphql -f query='
  mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $project, itemId: $item, fieldId: $field,
      value: { singleSelectOptionId: $option }
    }) { projectV2Item { id } }
  }' \
  -f project="$PROJECT_ID" -f item="$ITEM_ID" \
  -f field="<priority.id>" -f option="<priority.options.P1>"
```

Both mutations use `GH_PROJECT_TOKEN` (classic PAT with `repo` + `project` scopes) via `GH_TOKEN` env var.

## Files Changed

| File | Change |
|---|---|
| `skills/engineering/setup-harness-skills/output-steps.md` | Step 5: add field ID query + `project_fields` write to `harness.json` |
| `skills/engineering/setup-harness-skills/SKILL.md` | Document `project_fields` in the `.harness/` files section |
| `skills/engineering/harness-triage/SKILL.md` | Add board field sync step after agent brief is posted |
| `skills/engineering/harness-issues/SKILL.md` | Add board field sync step after each issue is created |
| `skills/engineering/setup-harness-skills/github-project.md` | Add `Priority` row to Custom fields table; note all three fields (Effort, Size, Priority) are set as board fields by skills |
