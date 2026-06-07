---
name: harness-verify-before-move
description: Comprehensive pre-phase-transition sweep. Verifies phase exit criteria, syncs code status (git/lint/build/tests), audits and cleans design docs, cleans implementation-notes, prunes stale documents and memory, syncs GitHub project state (milestones, issues, status labels, board), updates README, writes a fresh memory snapshot, then outputs a clean project snapshot. Use when completing a phase, before advancing to next phase, or when user says "verify before move", "clean up before moving", "sync everything", "project snapshot", "clean slate", "phase transition". Typically consumes ~8K–15K tokens / <10% of a context window.
---

# Harness — Verify Before Move

Comprehensive phase-exit sweep. Ten steps run in order: gate → code → docs → notes → unused files → memory cleanup → GitHub → README → memory write → snapshot.

**Destructive operations (delete, close, label-change) require explicit user confirmation. Never auto-apply.**

---

## When to trigger

- User says "move to next phase", "phase complete", "sync everything", "clean slate", "project snapshot", or any intent to advance
- You are about to update `position.phase` in `.harness/state.json`
- Before any handover that marks a phase closed

---

## Reference files

Load on demand — not all at once:

- **`references/github-sync.md`** — load at Step 7 (GitHub milestone, issue, board sync)
- **`references/doc-cleanup.md`** — load at Step 5 (unused document audit rules)

---

## Execution sequence

Run all 10 steps. Do not skip. Do not advance the phase until Step 1 passes.

**Every step reports its own confidence — not just its result.** Prefix each step's summary line with exactly one label:

- `[VERIFIED]` — you ran the check directly and have observable evidence (command output, file contents read, cross-reference traced end to end)
- `[ASSUMED]` — you ran the check, but the conclusion rests on inference or judgment rather than direct evidence (e.g., "this entry looks reversed" without tracing the actual code path)
- `[SKIPPED — <reason>]` — a precondition was missing and the check did not run at all

Do not default to `[VERIFIED]`. If you are not certain you checked something directly, it is `[ASSUMED]` or `[SKIPPED]`. Step 1 names Fuzzy Done, Proxy Signal, and Confidence Exit as anti-patterns to catch in the user's work — the same standard applies to this skill's own reporting. A step that silently downgrades to "looks fine" without naming that downgrade is committing the exact pattern it exists to catch.

---

### Step 1 — Phase exit gates

Identify current phase: `.harness/state.json` → `position.phase`. Fallback: GitHub issue labels → ask user.

Run the checklist for the current phase. **BLOCK on any failure — do not proceed to Step 2 until all BLOCKs are resolved.**

#### 01-discuss → 02-plan
- [ ] `.harness/phases/01-discuss/CONTEXT.md` exists and is non-empty
- [ ] No unresolved `?` or `TBD` in CONTEXT.md
- [ ] Scope is demoable — "user can do Y", not "improve X"
- [ ] User explicitly confirmed scope (not agent-inferred)

#### 02-plan → 03-execute
- [ ] `.harness/phases/02-plan/PLAN.md` exists
- [ ] Every task has an estimate (context windows) and at least one acceptance criterion
- [ ] At least one risk or assumption listed
- [ ] Total effort ≤ 8 context windows — if higher, BLOCK and require user to split

#### 03-execute → 04-verify
- [ ] All ACs have observable evidence (test name, CLI output, path — not "I think it works")
- [ ] `git status` is clean (run it, show output)
- [ ] Lint + build passes (run it, show output)
- [ ] `.harness/implementation-notes.md` updated with decisions from this phase
- [ ] No unresolved TODO/FIXME introduced this phase

#### 04-verify → done
- [ ] Every AC verified with named evidence
- [ ] No failing tests
- [ ] VERIFICATION.md or equivalent gate doc present in `.harness/phases/04-verify/`
- [ ] No open linked PRs in draft state

**Block format:**
```
BLOCK: [gate name]
  Reason: [one sentence — what is missing or wrong]
  Fix:    [one sentence — concrete next action, starts with a verb]
```

**Anti-patterns — name on detection:**

| Pattern | Signal | Response |
|---|---|---|
| **Fuzzy Done** | "seems to work" / "I think it's ready" | "This is Fuzzy Done — name observable evidence" |
| **Proxy Signal** | "tests pass" without running them | "This is a Proxy Signal — run the command and show output" |
| **Confidence Exit** | "I'm confident it's done" | "This is a Confidence Exit — confidence is not a gate" |

---

### Step 2 — Code status sync

Run each check and report output:

| Check | Command | Pass condition |
|---|---|---|
| Working tree | `git status --short` | Empty output |
| Uncommitted diff | `git diff --stat` | No output |
| Unpushed commits | `git log @{u}.. --oneline` | No output |
| Lint | (detect from `package.json` → `scripts.lint`, `Makefile`, `pyproject.toml`) | Exit 0 |
| Build | (detect from `scripts.build` or equivalent) | Exit 0 |
| Tests | (detect from `scripts.test` or equivalent) | All pass |

If lint/build/test commands are unknown, ask before running. Do not guess.

Output: pass/fail per row with one-line summary of failures.

---

### Step 3 — Design docs sync

Check each phase artifact for accuracy:

| Location | Expected doc | Verify |
|---|---|---|
| `.harness/phases/01-discuss/` | `CONTEXT.md` | Reflects current scope; no reversed decisions |
| `.harness/phases/02-plan/` | `PLAN.md` | Tasks match what was actually implemented |
| `.harness/phases/03-execute/` | Any ADRs or specs | Decisions match current code |
| `.harness/phases/04-verify/` | `VERIFICATION.md` | Present and accurate if phase is complete |

For each doc:
- Flag entries referencing features or decisions later reversed
- Flag broken cross-references (path in doc no longer exists on disk)

Do not edit without user confirmation. Output: one-line status per doc.

---

### Step 4 — Implementation notes cleanup

File: `.harness/implementation-notes.md`

1. If absent: note "implementation-notes.md not found — no cleanup needed" and skip.
2. Read all entries. Identify stale entries:
   - Items marked `[resolved]` or `[superseded]`
   - Decisions overridden by later entries in the same file
   - References to files or functions that no longer exist (spot-check 3–5 with `grep` or `glob`)
3. List stale entries to the user.
4. Ask: "Remove these stale entries? (y/n)" — remove only on confirmation.
5. If entries remain, verify the file has at least one dated entry from the current phase.

Output: "implementation-notes.md: N total entries, N stale [removed / kept by user]."

---

### Step 5 — Unused document cleanup

Load `references/doc-cleanup.md` for retention policy and safety rules.

Scan for candidates:
- `.harness/phases/XX-*/` scratch or draft files from phases two or more behind current
- Any `*.draft.md`, `*.bak`, `*.old`, `*.tmp` in `.harness/`
- Temporary output files with no cross-references in any doc or source file

Cross-reference check before flagging: grep the filename in CLAUDE.md/AGENTS.md, README.md, all SKILL.md files, and `.harness/**/*.md`. If any reference found — not a candidate.

Output candidate list:
```
Unused document candidates:
  .harness/phases/01-discuss/scratch-notes.md  — no cross-references
  .harness/temp-output.txt                     — no references found

Remove (r), archive to .harness/archive/ (a), or keep (k) each?
```

Default recommendation: archive first, delete after the next successful phase transition.

---

### Step 6 — Memory cleanup

Detect active memory system (check in order):
1. `MEMORY.md` in project root or `~/.claude/projects/*/memory/MEMORY.md`
2. `~/.agentmemory/` directory or agentmemory running on port 3111
3. `mem0` in `requirements.txt` / `package.json` / `pyproject.toml`

**File-based (MEMORY.md):**
1. Read all entries.
2. Flag stale entries: decisions reversed, files no longer existing, phases completed 2+ phases ago with no still-valid content.
3. List to user. Ask: "Remove these stale entries? (y/n)."
4. Remove only on confirmation.

**agentmemory / mem0:**
1. Query for project/task-related entries.
2. Flag entries older than the current phase with no confirmed still-valid status.
3. List candidates — note "delete via memory system UI or API; cannot auto-remove."

Output: "Memory: N entries total, N stale [removed / flagged for review]."

If no memory system found: note "No memory system detected — skip." (Not a blocker.)

---

### Step 7 — GitHub project sync

Load `references/github-sync.md` for full operation details.

**Skip entirely if `docs/agents/issue-tracker.md` does not exist.**

Read `.harness/config.json` or `docs/agents/issue-tracker.md` for `owner`, `repo`, `project_id`, `milestone`.

Sync areas (details in reference file):
1. **Milestone** — verify % complete matches actual closed/open issue ratio
2. **Issue status labels** — every open milestone issue has exactly one `status:*` label
3. **Project board** — issue columns match their status labels
4. **Stale issues** — open, no activity for >7 days, no `status:blocked` or `status:on-hold`
5. **Linked PRs** — no merged PRs with still-open linked issues; no draft PRs linked to issues being closed

For each discrepancy, output the correction command. **Run nothing without user approval.**

---

### Step 8 — README update

Read the project's `README.md` (or equivalent root readme).

Check:
- [ ] Setup/install instructions still accurate (commands match current project structure)
- [ ] Feature list reflects shipped state — no "coming soon" for shipped features, no entries for dropped features
- [ ] Any version, status, or coverage badges are current
- [ ] Phase-transition artifacts (e.g. "WIP" banners) are removed

Propose minimal diffs. Apply only on user approval. If README is accurate: "README: no changes needed."

---

### Step 9 — Memory write

Write a project snapshot to the active memory system.

Check `.claude/settings.json` hooks first — if a Stop hook writes memory automatically, **skip to avoid duplicates**.

Otherwise write a dated entry containing:
- Phase completed and next phase
- Key decisions from this phase (from implementation-notes.md, condensed)
- What shipped (from VERIFICATION.md or ACs)
- Any non-obvious constraints or invariants discovered this phase

Append to `MEMORY.md`, or call the configured memory API. Budget: <3% context.

---

### Step 10 — Project snapshot + state sync

Write state:
- `.harness/state.json` → `position.phase` = next phase, `session.status` = `"idle"`, `position.stopped_at` = "Phase [current] complete — advancing to [next]"
- `.harness/phases/XX-current/.continue-here.json` → `completed_work` array, `next_action` (first concrete step of next phase, starts with a verb)

Post GitHub progress comment if `docs/agents/issue-tracker.md` exists and active task has an issue number:

```
## Phase transition — YYYY-MM-DD HH:mm

**From:** [current phase]  **To:** [next phase]
**Confidence:** [N] verified · [N] assumed · [N] skipped — see snapshot below for which

**Exit gates:** [VERIFIED] all [N] passed
**Code:** [VERIFIED] git clean · lint · build · tests
**Docs:** [VERIFIED/ASSUMED] CONTEXT.md · PLAN.md · VERIFICATION.md
**GitHub:** [VERIFIED/SKIPPED — reason] milestone [N]%  |  [N] label corrections  |  [N] board moves
**README:** [VERIFIED] [updated / no changes]
**Memory:** [VERIFIED/SKIPPED — reason] [N] stale removed, snapshot written

**Next step:** [next_action from .continue-here.json]

---
_🤖 Posted by `/harness-verify-before-move` (AI-generated)_
```

Output final snapshot to user:

```
## Project Snapshot — [current] → [next phase]
[YYYY-MM-DD HH:mm]

Confidence: [N] verified · [N] assumed · [N] skipped
(every [ASSUMED] or [SKIPPED] line below names what wasn't directly checked, and why)

[VERIFIED] Code
  git: clean | lint: pass | build: pass | tests: N passed

[VERIFIED] Phase gates
  All N gates: PASSED

[VERIFIED/ASSUMED] Design docs
  CONTEXT.md: current | PLAN.md: current | VERIFICATION.md: present
  (if ASSUMED — name which entries were inferred rather than traced against code)

[VERIFIED/SKIPPED — reason] Implementation notes
  N entries, N stale removed

[VERIFIED/ASSUMED] Unused documents
  N candidates — N removed, N archived, N kept
  (if ASSUMED — cross-reference was grep-based; name reference types not covered, e.g. code comments, CI configs)

[VERIFIED/SKIPPED — reason] Memory
  N entries, N stale removed | snapshot written

[VERIFIED/SKIPPED — reason] GitHub
  Milestone: [name] — N% complete
  N issues synced | N label corrections | N board moves

[VERIFIED] README
  [N sections updated / no changes]

State synced
  .harness/state.json → phase: [next]
  .harness/phases/[XX-current]/.continue-here.json → written
  GitHub #N comment posted

Ready for /session-start → [next phase].
```

---

## Graceful degradation

| Missing | Action |
|---|---|
| No `.harness/state.json` | Prompt "Run /setup-harness-skills first or tell me the current phase" |
| No `docs/agents/` | Skip Step 7 (GitHub sync) |
| No memory system | Skip Step 6 cleanup; write decisions in `.continue-here.json` decisions_made |
| No `README.md` | Skip Step 8 |
| No GitHub remote | Skip all GitHub operations silently |
| Unknown lint/build/test commands | Ask user before running Step 2 |
| Phase exit gates BLOCKED | Stop at Step 1; do not run Steps 2–10 |
