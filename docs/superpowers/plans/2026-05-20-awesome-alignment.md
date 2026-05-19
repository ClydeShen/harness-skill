# Awesome-Harness Alignment Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the gaps between this skill's detection logic and the community consensus documented in awesome-harness-engineering.

**Architecture:** Four targeted file edits (detect.md, SKILL.md, universal-snippets.md, evals.json) — no new files. Every change is backwards-compatible with the existing four evals.

**Tech Stack:** Markdown only — no build step.

---

## File Map

| File | Change |
|---|---|
| `skills/harness-engineering/references/detect.md` | Add AGENTS.md row to major gaps; add observability row to minor gaps; update CLAUDE.md gap note to recognise AGENTS.md as equivalent |
| `skills/harness-engineering/SKILL.md` | Phase 1: add AGENTS.md check (step 9); Phase 2 Q2: fold in brownfield sub-question; Interview branch table Q2: add brownfield row; spec workflow: conditional major gap note |
| `skills/harness-engineering/references/universal-snippets.md` | Strengthen Stop hook prompt to require state summary |
| `skills/harness-engineering/evals/evals.json` | Add eval IDs 5 (brownfield) and 6 (AGENTS.md) |

---

## Chunk 1: detect.md edits

### Task 1: Add AGENTS.md as major gap + update CLAUDE.md gap detection

**Files:**
- Modify: `skills/harness-engineering/references/detect.md`

Current major gap table has a "No CLAUDE.md" row. We need:
- The gap to trigger only when NEITHER `CLAUDE.md` NOR `AGENTS.md` is present.
- A new row for "No AGENTS.md when CLAUDE.md is absent" — but more precisely: reframe as "No agent instruction file".

- [ ] **Step 1: Edit the "No CLAUDE.md" row in the Major gaps table**

Find this exact text in `detect.md`:
```
| No CLAUDE.md | `CLAUDE.md` absent | No persistent context anchor — every session starts blind |
```

Replace with:
```
| No agent instruction file | `CLAUDE.md` absent AND `AGENTS.md` absent | No persistent context anchor — every session starts blind |
```

- [ ] **Step 2: Add detection note for AGENTS.md equivalence**

After the Gap Classification section header and before the Major gaps table, add a callout note. Find:
```
### Major gaps (each counts toward the Q3 threshold)
```

Insert above it:
```
> **Note:** `AGENTS.md` is treated as fully equivalent to `CLAUDE.md`. If either is present, the "agent instruction file" gap is closed. Apply all CLAUDE.md quality checks (line count, conditional tags, rules directory) to whichever file is present.

```

- [ ] **Step 3: Add observability as minor gap**

Append to the Minor gaps table (after the last row, before the closing `---`):

```
| No observability tooling | None of: `agentops` in deps, `agenttrace` installed, structured logging in entry-point files | Cost spikes, tool failures, and regressions go undetected across sessions |
```

- [ ] **Step 4: Verify the file reads cleanly**

Read `references/detect.md` end-to-end to confirm no broken table formatting.

- [ ] **Step 5: Commit**

```
git add skills/harness-engineering/references/detect.md
git commit -m "feat(detect): AGENTS.md equivalence, observability minor gap"
```

---

## Chunk 2: SKILL.md edits

### Task 2: Phase 1 — add AGENTS.md check

**Files:**
- Modify: `skills/harness-engineering/SKILL.md`

- [ ] **Step 1: Add AGENTS.md check to Phase 1 scan list**

Find this block in SKILL.md:
```
6. Check CLAUDE.md: exists? line count under 200? contains `<important if>` tags or `.claude/rules/`?
7. Check rules directory: `.claude/rules/` — exists if CLAUDE.md is over 100 lines?
8. Check spec workflow: `docs/superpowers/specs/` directory exists?
8. Check UI harness (frontend stack only): `DESIGN.md` exists?
```

Replace with (fix duplicate `8.`, add step 9):
```
6. Check agent instruction file: `CLAUDE.md` OR `AGENTS.md` present? Check whichever exists: line count under 200? contains `<important if>` tags or `.claude/rules/`?
7. Check rules directory: `.claude/rules/` — exists if the instruction file is over 100 lines?
8. Check spec workflow: `docs/superpowers/specs/` directory exists?
9. Check UI harness (frontend stack only): `DESIGN.md` exists?
```

### Task 3: Phase 2 Q2 — add brownfield sub-question

- [ ] **Step 2: Update Q2 trigger condition and text**

Find:
```
**Q2 — Ask only if no branch protection or PR workflow detected:**
> "Solo dev or team?"
```

Replace with:
```
**Q2 — Ask only if no branch protection or PR workflow detected:**
> "Solo dev or team? And is this an existing codebase you're inheriting, or are you starting from scratch?"
```

- [ ] **Step 3: Add brownfield row to Interview Branch Decisions Q2 table**

Find the Q2 table in the "Interview Branch Decisions" section:
```
| **Solo** | CI snippet uses `push: branches: [main]` trigger only. Do not recommend branch protection rules, PR review gates, or `pull_request` trigger. |
| **Team** | CI snippet adds `pull_request: branches: [main]` trigger. Add a note: "Consider adding branch protection on main (require PR + passing CI before merge)." |
```

Replace with:
```
| **Solo** | CI snippet uses `push: branches: [main]` trigger only. Do not recommend branch protection rules, PR review gates, or `pull_request` trigger. |
| **Team** | CI snippet adds `pull_request: branches: [main]` trigger. Add a note: "Consider adding branch protection on main (require PR + passing CI before merge)." |
| **Brownfield (inherited codebase)** | Soften pre-commit hook recommendation: suggest adding hooks incrementally rather than fixing all existing violations at once. Warn that a lint run may surface hundreds of pre-existing errors — recommend baselining them first with `eslint --fix` or `ruff --fix` on a dedicated cleanup commit before enabling the hook. |
```

### Task 4: Upgrade spec workflow to conditional major gap

- [ ] **Step 4: Add a note in the Output rules section**

Find in Phase 3 Output:
```
- Rank gaps by impact: verification gap > CLAUDE.md quality > CI > pre-commit > memory
```

Replace with:
```
- Rank gaps by impact: verification gap > agent instruction file quality > CI > pre-commit > memory
- Spec workflow (`docs/superpowers/specs/` absent) is a **minor gap by default** but escalates to **major gap** when Q1 answer is "long / autonomous (>1 hr)" — include it in the top-5 for those tasks
```

- [ ] **Step 5: Commit**

```
git add skills/harness-engineering/SKILL.md
git commit -m "feat(skill): AGENTS.md check, brownfield Q2, spec gap escalation"
```

---

## Chunk 3: universal-snippets.md — Stop hook

### Task 5: Strengthen the Stop hook prompt

**Files:**
- Modify: `skills/harness-engineering/references/universal-snippets.md`

- [ ] **Step 1: Replace Stop hook prompt**

Find:
```
            "prompt": "Before ending this turn: have you run the project build and lint? If this was UI work, have you opened the feature in a browser? If any check is outstanding, complete it now."
```

Replace with:
```
            "prompt": "Before ending this turn: (1) Run the project build and lint — fix any errors now, not later. (2) If this was UI work, open the feature in a browser and confirm the behavior is observable end-to-end. (3) Write a two-sentence status summary: what was changed and what the next concrete step is. Complete all outstanding checks before finishing."
```

- [ ] **Step 2: Commit**

```
git add skills/harness-engineering/references/universal-snippets.md
git commit -m "feat(snippets): strengthen Stop hook — add status summary requirement"
```

---

## Chunk 4: evals.json — two new scenarios

### Task 6: Add brownfield eval (ID 5)

**Files:**
- Modify: `skills/harness-engineering/evals/evals.json`

- [ ] **Step 1: Add eval 5 to the evals array**

Append after the closing `}` of eval ID 4, before the final `]`:

```json
,
    {
      "id": 5,
      "prompt": "I'm taking over a Next.js TypeScript project that's been running in production for 2 years. It has roughly 50,000 lines of code, no .pre-commit-config.yaml, and eslint currently reports 340 errors. I want to start using Claude Code on it. What harness should I set up, and where should I start?",
      "expected_output": "The skill should recognise this as a brownfield / inherited codebase scenario. It should NOT recommend fixing all 340 ESLint errors as a prerequisite. It should recommend incremental (ratcheted) adoption: run eslint --fix on a dedicated cleanup commit to baseline existing violations, then enable the pre-commit hook going forward. Stop hook and CI gaps remain highest priority regardless.",
      "files": [
        "Next.js TypeScript project with ~50k lines",
        "no .pre-commit-config.yaml",
        "eslint reports 340 errors on existing code",
        "no .claude/settings.json"
      ],
      "expectations": [
        "Does NOT instruct the user to fix all 340 ESLint errors before starting",
        "Recommends a baseline / ratchet approach for pre-commit hooks on inherited code",
        "Still identifies missing Stop hook as the highest-priority gap",
        "Acknowledges this is an inherited / brownfield codebase and adjusts recommendations accordingly",
        "Suggests a dedicated cleanup commit to reduce lint noise before enabling the hook"
      ]
    }
```

### Task 7: Add AGENTS.md equivalence eval (ID 6)

- [ ] **Step 2: Add eval 6 to the evals array**

Append after eval ID 5:

```json
,
    {
      "id": 6,
      "prompt": "My project already has an AGENTS.md file at the root that documents the stack, key commands, architecture, and coding conventions for AI agents. It's about 80 lines. Do I still need a CLAUDE.md? Are there any harness gaps I should fix?",
      "expected_output": "The skill should recognise AGENTS.md as fully equivalent to CLAUDE.md. It must NOT flag 'No CLAUDE.md' as a gap. It should apply the same quality checks to AGENTS.md: 80 lines is under the 200-line ceiling but over the 60-line target — acceptable. It should then check for and report on other gaps (hooks, CI, init.sh, etc.) as normal.",
      "files": [
        "AGENTS.md at project root, ~80 lines",
        "no CLAUDE.md",
        "no .claude/settings.json"
      ],
      "expectations": [
        "Does NOT flag missing CLAUDE.md as a harness gap",
        "Explicitly recognises AGENTS.md as equivalent to CLAUDE.md",
        "Checks AGENTS.md quality: line count, conditional tags, .claude/rules/ if over 100 lines",
        "Proceeds to report other harness gaps (hooks, CI, etc.) as normal",
        "Does not recommend creating a CLAUDE.md alongside AGENTS.md (YAGNI)"
      ]
    }
```

- [ ] **Step 3: Verify the JSON is well-formed**

```bash
python -c "import json; json.load(open('skills/harness-engineering/evals/evals.json'))"
```

Expected: no output (no parse errors).

- [ ] **Step 4: Commit**

```
git add skills/harness-engineering/evals/evals.json
git commit -m "feat(evals): add brownfield (id=5) and AGENTS.md (id=6) scenarios"
```

---

## Done Criteria

- [ ] `detect.md`: AGENTS.md equivalence note present; "No agent instruction file" row in major gaps; observability in minor gaps
- [ ] `SKILL.md`: Phase 1 step 9 present; Q2 includes brownfield sub-question; brownfield row in branch table; spec gap escalation rule in Phase 3
- [ ] `universal-snippets.md`: Stop hook prompt contains "status summary" language
- [ ] `evals.json`: 6 evals total; `python -c "import json; json.load(...)"` passes
- [ ] All four existing evals still satisfied (no regression)
- [ ] 4 commits, one per chunk
