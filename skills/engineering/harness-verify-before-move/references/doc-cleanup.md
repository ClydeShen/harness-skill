# Document Cleanup Rules

Loaded by `harness-verify-before-move` Step 5.

## What counts as a cleanup candidate

A document is a **candidate** only if ALL of the following are true:

1. Not referenced by any `SKILL.md`, `PLAN.md`, `CONTEXT.md`, `VERIFICATION.md`, `README.md`, or source file (check with `grep -rl <filename> .`)
2. Not `.continue-here.json` — always keep, needed for interrupted-session recovery
3. Not `state.json`, `config.json`, or any file named in the harness schema
4. Not modified during the current phase (modification = still active)
5. From a phase two or more behind the current phase (see retention table below)

---

## Safety rules

- **Never auto-delete.** Always list candidates and ask for confirmation.
- **Never delete `.continue-here.json`** from any phase — recovery artifact.
- **Never delete current-phase or previous-phase artifacts** — only phases 2+ behind current.
- **Prefer archive over delete** when user is unsure — move to `.harness/archive/YYYY-MM-DD/`.

---

## Phase artifact retention policy

| Phase relative to current | Keep always | Can be candidates |
|---|---|---|
| Current phase | Everything | Nothing |
| One phase back | Everything | Nothing |
| Two or more phases back | `.continue-here.json`, `CONTEXT.md`, `PLAN.md`, `VERIFICATION.md` | `scratch*.md`, `*.draft.md`, `*.bak`, `*.tmp`, `*.old`, unlisted output files |
| All phases complete (done) | `CONTEXT.md`, `PLAN.md`, `VERIFICATION.md` | Everything else |

---

## Cross-reference check (required before flagging)

Before marking a document as a candidate, grep for its filename in:

```bash
grep -rl "<filename>" \
  CLAUDE.md AGENTS.md README.md \
  .harness/phases/**/*.md \
  skills/**/*.md \
  2>/dev/null
```

If any reference is found — **not a candidate**. Remove it from the list.

---

## Candidate output format

Present as an interactive list:

```
Unused document candidates:
  [r/a/k] .harness/phases/01-discuss/scratch-notes.md
            Last modified: YYYY-MM-DD | No cross-references found
  [r/a/k] .harness/temp-output.txt
            Last modified: YYYY-MM-DD | No cross-references found

Options per file:
  r = remove (permanent delete)
  a = archive to .harness/archive/YYYY-MM-DD/<filename>
  k = keep (exclude from future candidates this phase)

Enter choice for each (e.g. "a r k"):
```

Default recommendation: `a` (archive). Never default to `r`.

---

## Archive operation

```bash
mkdir -p .harness/archive/YYYY-MM-DD
mv <file> .harness/archive/YYYY-MM-DD/<filename>
```

The archive directory itself is retained indefinitely — it is documentation of what was cleaned and when. It is never a cleanup candidate.
