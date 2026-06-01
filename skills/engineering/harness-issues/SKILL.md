---
name: harness-issues
description: Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices with enforced AC templates, creation gates, and dual output to GitHub Issues + PLAN.md. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

The issue tracker and triage label vocabulary should have been provided to you — run `/setup-harness-skills` if not.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue to the issue tracker. Use the issue body template below. These issues are considered ready for AFK agents, so publish them with the correct triage label unless instructed otherwise.

#### Milestone issue discovery

In modern GitHub project planning, a "Milestone" is an issue with issue type `Milestone` (or the org's equivalent parent type), not GitHub's legacy Milestone progress-tracker feature. Before creating any issues, check whether a parent milestone issue already exists:

```bash
# List open issues typed as Milestone (adjust type name to match org config)
gh api "repos/{owner}/{repo}/issues?state=open&type=Milestone" \
  --jq '[.[] | {number: .number, title: .title, type: .issue_type.name}]'
```

- **No milestone-type issues found:** skip — create issues without a parent link. Do not fall back to the legacy `--milestone` flag.
- **One milestone issue and context maps to it:** note it; new issues will be linked as sub-issues of it in the Sub-issue linkage step below.
- **Multiple milestone issues or ambiguous mapping:** present the list and ask the user which to group under (or "none"). Do not guess.

**Note:** `gh issue create` has no `--type` flag. Set issue type after creation via REST API:
```bash
gh api repos/{owner}/{repo}/issues/<number> --method PATCH -f type="<issue_type_name>"
```
Type assignment failure is non-blocking — print `⚠️ Type not set for #N: <error>` and continue.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

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

All project board operations use **GraphQL** via `gh api graphql`. The `singleSelectOptionId` values for Size and Priority are stored in `project_fields` inside `.claude/harness.json` — fetch them once at the start of this sequence rather than querying the API each time.

1. Read `github.project_v2_id` from `.claude/harness.json` — this is the `projectId` (GraphQL node ID, e.g. `PVT_...`) for all mutations.
2. Capture the issue number from `gh issue create` output.
3. Fetch issue GraphQL node ID: `gh issue view N --json id --jq '.id'` → returns a node ID like `I_kwDO...`.
4. Add to project board:
   ```bash
   gh api graphql -f query='
     mutation {
       addProjectV2ItemById(input: {projectId: "PVT_..." contentId: "I_kwDO..."}) {
         item { id }
       }
     }'
   ```
   Capture the returned `item.id` (project item node ID, e.g. `PVTI_...`) — required for field updates.
5. Parse Effort integer from the issue body (`Estimate: **N context window(s)**` line).
6. Derive Size from Effort using the mapping above.
7. Resolve Priority from labels: `priority:p1 → P1`, `priority:p2 → P2`, `priority:p3 → P3`; skip if no priority label present.
8. Update fields (one call per field):
   ```bash
   gh api graphql -f query='
     mutation {
       updateProjectV2ItemFieldValue(input: {
         projectId: "PVT_..."
         itemId: "PVTI_..."
         fieldId: "FIELD_ID"
         value: { singleSelectOptionId: "OPTION_ID" }
       }) { projectV2Item { id } }
     }'
   ```
   Call for Effort (number field, use `value: { number: N }`), Size, and Priority if resolved.
9. Print per-issue confirmation: `✅ #N board fields — Effort: N, Size: X, Priority: Pn / not set`.

**Error handling:** Mutation failure is non-blocking — print `⚠️ Board field update failed for #N: <error>` and continue to the next issue.

#### Sub-issue and dependency linkage

After all issues are created, establish GitHub parent-child relationships so dependencies are visible in GitHub Projects. Sub-issues is GA (no preview header needed; requires write access).

**Critical:** `sub_issue_id` takes the issue's **database ID** (the `id` field, a large integer like `7890123456`), NOT the issue number. Fetch it after each `gh issue create`:

```bash
# Fetch database ID for a newly created issue by its number
gh api repos/{owner}/{repo}/issues/<number> --jq '.id'
```

**Case 1 — Source was an existing issue #N (`/harness-issues #N`), OR a milestone-type parent issue was identified in the discovery step:**
For each created issue, link it as a sub-issue of that parent:
```bash
gh api repos/{owner}/{repo}/issues/N/sub_issues \
  --method POST \
  -F sub_issue_id=<child_database_id>
```

**Case 2 — Dependency between newly created issues (B is "Blocked by" A):**
For each such pair, link B as a sub-issue of A:
```bash
gh api repos/{owner}/{repo}/issues/<A_number>/sub_issues \
  --method POST \
  -F sub_issue_id=<B_database_id>
```

**Guard:** If the API returns a non-2xx response:
```
⚠️ Sub-issue linkage failed for #A → #B: <error>. Check write permissions and that both issues are in the same organization.
```
Sub-issue linkage failure is non-blocking — issue creation is not affected.

**Confirmation per pair:** `✅ #B linked as sub-issue of #A`

<issue-template>
## Parent

A reference to the parent issue on the issue tracker (if the source was an existing issue, otherwise omit this section).

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking ticket (if any)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT close or modify any parent issue.

---

## User story format

Each issue must follow BA best practices:

**Title:** `[type]: short imperative description` (e.g. `feature: user can reset password via email`)

**Body:** As a [role], I want [capability], so that [benefit].

### Acceptance Criteria
| # | Criterion | Type | Source |
|---|---|---|---|
| 1 | Given X, when Y, then Z | happy path | Spec §N.N |
| 2 | Given X, when error, then W | sad path | User statement YYYY-MM-DD |

Minimum 1 happy path + 1 sad path per story. Valid source types (exactly three):
1. **Spec section** — cite section number (e.g. "Spec §3.2")
2. **Explicit user statement** — cite session date (e.g. "User statement 2026-05-24")
3. **Named best practice** — cite a named reference: URL, named pattern, or specific line in CLAUDE.md/CONTEXT.md. An uncited "best practice" claim is not valid.

### Definition of Done
- [ ] All AC pass (verified by agent or CI)
- [ ] PR merged to main
- [ ] No regressions in related tests
- [ ] Implementation notes written if agent deviated from spec

### Effort estimate
Unit = token budget. 1 ≈ 150K–200K tokens (single slice). See [Effort calibration table](../harness-triage/references/effort-calibration.md).

---

**What vs. How:** This story describes WHAT the system should do. HOW to implement it is determined by the Execution agent when it reads this issue. Do not add technical implementation details, file paths, or code snippets.

## Enforced issue template

Every issue created by `/harness-issues` must follow this exact structure:

```markdown
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

## HITL/AFK routing

| Category | Definition | Label applied |
|---|---|---|
| **AFK** | Every AC item traces to a cited source; no gaps in the requirement → AC → DoD chain | `status:ready-for-agent` |
| **HITL** | At least one AC item lacks a traceable source, or the chain has a gap, or genuine ambiguity exists | `status:needs-review` (written but unconfident) or `status:needs-prd` (story not yet writable) |

An agent that cannot populate the Source column for every AC row must classify the issue as HITL.

## Three creation gates

Check each story against all three gates before creating the issue:

1. **Estimable gate:** A story that cannot be estimated must be refined before the issue is created.
2. **Size gate:** A story estimated at >8 context windows must be split. Above this, scope is too large to track and hand over reliably. (8 windows ≈ 8 sessions of focused work — handoff drift compounds beyond this point)
3. **Vertical slice gate:** Every issue must deliver a **demoable user-facing outcome**. Ask: *"Can this story be demonstrated to a stakeholder end-to-end without implementing any other story first?"* If no → restructure into a vertical slice before creation.

### 6. Write .harness/phases/02-plan/02-PLAN.md (dual output)

In addition to GitHub Issues, write a GSD PLAN.md file. One task block per issue:

```markdown
## Task N: [title]

**Type:** feature | bug | chore | spike
**Effort:** N context window(s) (token budget: 1 = ~150K–200K tokens / single slice; 2 = ~300K–400K / 1 phase; 3 = ~500K–700K / full feature; 4+ = epic)

### What to build
[User-facing outcome, one sentence]

### Acceptance criteria
- [ ] [criterion]

### Files likely involved
[leave blank — agent decides HOW]
```

Path: `.harness/phases/02-plan/02-PLAN.md`. Create `.harness/phases/02-plan/` if absent.

## Mid-session execution rules

execute phase agents reading these issues must:
1. **Commit after each AC item completes** — the git log is the durable in-session progress record.
2. **Post a progress comment after each AC item completes** — format: `Progress [timestamp]: Completed AC #N — [one line summary]. Remaining: [list].` This survives mid-session interruptions without a clean handover.
3. **PLAN.md is a local mirror** — GitHub Issues are the canonical human-visible record. PLAN.md is the GSD-compatible local record. Both are written simultaneously. If GitHub is not configured, write PLAN.md only.
