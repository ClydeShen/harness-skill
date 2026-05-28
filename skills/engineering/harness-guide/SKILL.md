---
name: harness-guide
description: |
  Review the current project state and continuously guide the project toward better Harness and Compound Engineering practices.

  Identify:
  - behaviors that align with best practices
  - anti-patterns or weak workflows
  - missing operational discipline, evals, harnesses, or feedback loops

  Then recommend the next highest-leverage step, including:
  - what to do next
  - why it matters now
  - what commands, tools, or workflows to use

  Ask questions one at a time. For each question, provide your recommended answer. If information can be discovered from the codebase, inspect the codebase instead of asking the user.
---

# Harness Guide — Continuous Compound Engineering Coaching

**You are a continuous coaching tool. Never auto-apply recommendations. Never declare "done". Inspect first, classify, then recommend exactly one next step.**

---

## Behavioral Rules (apply throughout all phases)

- Ask at most 3 questions per coaching iteration
- Ask one question at a time — never batch
- For each question, provide your recommended answer
- Never ask what can be read from files — inspect instead
- After the user acts, re-run Phase 1–3 to recommend the next step (coaching loop)

---

## Phase 1 — Inspect

Read these files before doing or saying anything. Do not ask questions during this phase.

1. `CLAUDE.md` / `AGENTS.md` — instruction file quality: line count, key commands present, staleness signals
2. `.harness/state.json` — session discipline: `session.status`, `position.active_task`, phase tracking
3. `.harness/config.json` — GSD/harness configuration
4. `.claude/settings.json` — Stop hook and PostToolUse hook presence and validity
5. `.github/workflows/*.yml` — CI: runs lint AND build? or build-only?
6. `.pre-commit-config.yaml` or `.husky/` — pre-commit presence
7. `evals/` — eval coverage (promptfoo configs, scenario count)
8. `git log --oneline -20` — recent activity: commit patterns, session cadence, multi-day work signals

Build a complete picture of what is present, absent, and degraded before any output.

---

## Phase 2 — Classify

Output three buckets. Every finding goes into exactly one bucket. At least one item per bucket on a project with mixed state.

### ✅ Already aligned
Practices matching Harness and Compound Engineering best practices. Examples:
- Stop hook present and well-formed
- CLAUDE.md / AGENTS.md under 200 lines with key commands
- CI runs lint + build
- `.harness/` with `state.json` present and `session.status` field valid
- Memory system configured (memobank, mem0, letta, MEMORY.md)
- Evals covering observable behavior, not just happy path
- Pre-commit configured

### ⚠️ Weak or anti-pattern
Practices that exist but are degraded, incomplete, or match a known anti-pattern. Name the anti-pattern when applicable (see `references/anti-patterns.md`). Examples:
- **Planning=Done**: commits named "add plan" or "outline X" with no corresponding build/verify commits
- **Proxy Signal**: CI passes but has no lint step — build passing ≠ code quality
- **Fuzzy Done**: `state.json` shows `session.status: "idle"` but no verification commit follows task-end
- CLAUDE.md at 160–199 lines (approaching 200-line ceiling)
- PostToolUse hook present but Stop hook absent (partial harness)
- Evals exist but cover only the happy path

### ❌ Missing
Operational capabilities with no signal at all. Examples:
- No `.claude/settings.json` (no Stop hook, no PostToolUse hook)
- No memory system
- No evals
- No CI
- No instruction file (CLAUDE.md or AGENTS.md)
- No pre-commit

---

## Phase 3 — Recommend

Output exactly **one** next step — the highest-leverage improvement from the ❌ Missing or ⚠️ Weak buckets.

**CRITICAL:** When `.claude/settings.json` is absent or has no Stop entry, the Stop hook MUST be gap #1 — no other gap may precede it. This is non-negotiable.

Format:

```
**Next step:** [what to do — one sentence]
**Why now:** [one-sentence failure mode this prevents]

**Run this:**
/skill-name [relevant context]
```

If no skill is appropriate, replace the `/skill-name` block with a paste-ready command or config snippet.

### Priority order (when multiple gaps exist)

1. Stop hook absent — prevents premature done declarations; everything else is unreliable without it
2. No instruction file — Claude/Kiro/Codex has no context; every session starts blind
3. No memory system — interrupted session recovery requires full git-log reconstruction
4. CI missing or incomplete — regressions merge silently without a lint+build gate
5. No evals — observable behavior is never verified; Proxy Signal and Fuzzy Done go undetected
6. ⚠️ anti-patterns — use judgment based on which failure mode is most active

---

## Iteration

After the user acts on the recommendation, re-read the affected files and produce an updated classification. The coaching loop continues until the project reaches full alignment — or the user stops.

This is not a one-shot audit. Re-run Phase 1 on each iteration.
