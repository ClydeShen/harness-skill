# Plan: Board Fields Sync

**Spec:** `docs/superpowers/specs/2026-05-29-board-fields-sync-design.md`
**Created:** 2026-05-29

---

## Task 1: setup-harness-skills — populate project_fields in harness.json

**Type:** feature
**Effort:** 1 context window(s)
**GitHub:** #11

### What to build
`setup-harness-skills` Step 5 creates Priority and Size board fields if absent, queries all three field IDs from the board, and writes them to `.claude/harness.json` under `project_fields`. Also updates `SKILL.md` and `github-project.md` to document the new key and Priority field.

### Acceptance criteria
- [ ] Priority (P1/P2/P3) and Size (XS/S/M/L/XL) fields created on board if absent
- [ ] `harness.json` gains `project_fields` with `priority`, `size`, and `effort` sub-keys
- [ ] Idempotent: re-running Step 5 does not overwrite existing `project_fields` keys
- [ ] Missing fields produce omitted sub-keys, not errors
- [ ] `SKILL.md` and `github-project.md` updated

### Files likely involved

---

## Task 2: harness-triage — sync board fields after agent brief

**Type:** feature
**Effort:** 1 context window(s)
**GitHub:** #12
**Blocked by:** Task 1 (#11)

### What to build
After `harness-triage` posts an agent brief, read `project_fields` from `harness.json`, parse Effort from the brief, ask maintainer once for Priority, then set Effort, Size, and Priority on the board item via GraphQL mutations.

### Acceptance criteria
- [ ] Effort (windows) set from parsed brief value
- [ ] Size derived and set from Effort using shared mapping
- [ ] Maintainer asked once for Priority; skip leaves field unset
- [ ] Missing `project_fields` prints warning and skips silently
- [ ] Mutation failure is non-blocking

### Files likely involved

---

## Task 3: harness-issues — sync board fields after issue creation

**Type:** feature
**Effort:** 1 context window(s)
**GitHub:** #13
**Blocked by:** Task 1 (#11)

### What to build
After each `gh issue create`, add the issue to the project board, parse Effort from the issue body, derive Size, resolve Priority from labels, and set all three fields via GraphQL mutations.

### Acceptance criteria
- [ ] Issue added to board via `addProjectV2ItemByContentId`
- [ ] Effort (windows) parsed from `Estimate: **N context window(s)**` line
- [ ] Size derived and set from Effort
- [ ] Priority set from `priority:p1/p2/p3` label if present; omitted if absent
- [ ] Missing `project_fields` prints warning and skips silently
- [ ] Mutation failure is non-blocking per issue

### Files likely involved
