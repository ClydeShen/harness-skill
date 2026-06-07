# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
    3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Harness Discipline

**Long-running work fails silently. Epistemic gaps compound into errors. Make both kinds of boundary explicit.**

- Don't fabricate. Every factual claim must trace to observed evidence, documentation, or established best practice. Confidence is not a source — if you cannot ground a claim, say so rather than presenting it as fact.
- It's OK not to know. Say so explicitly instead of guessing. Proactively surface information gaps and ask what you need to proceed — don't fill them with plausible-sounding assumptions.
- While implementing a spec, maintain a running `.harness/implementation-notes.md` capturing: decisions made that weren't covered by the spec, things that had to change from the original plan, tradeoffs you made, and anything else the human should know.
- Exit criteria must be observable: a gate that passed, not a feeling that it's done. Name the anti-patterns: Fuzzy Done, Proxy Signal, Confidence Exit.
- State lives outside the agent. The source of truth is the issue tracker, the handoff document, the config file — not working memory.

## 6. Long-Task Checkpointing

**Checkpoint after every committed chunk.**

For multi-step tasks spanning more than one commit:

- Write progress to `.harness/state.json` (`position.stopped_at`) after each chunk completes.
- Commit the checkpoint alongside the work — never leave state and code out of sync.
- If interrupted, the next session reads the checkpoint and resumes from the last known-good commit.

Do not run long autonomous loops without a checkpoint strategy.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, clarifying questions come before implementation rather than after mistakes, and long-running sessions hand off cleanly without lost context.

## Project Context

Curated skill collection for compound engineering workflows, packaged as a Claude Code / Codex plugin. 14 skills across `skills/engineering/` and `skills/productivity/`.
Install: `bash scripts/link-skills.sh` (Linux/Mac) · `powershell -File scripts\link-skills.ps1` (Windows)

## Key Commands

```bash
# Run all evals (requires promptfoo on PATH + llamacpp at localhost:8080):
python evals/run_evals.py

# One skill:
python evals/run_evals.py --skill harness-audit

# Filter by eval description:
python evals/run_evals.py --skill harness-audit --filter "#2"

# Run promptfoo directly:
cd evals/promptfoo && promptfoo eval --config harness-audit.yaml
```

**Before committing any skill change:** run `python evals/run_evals.py --skill <name>` and confirm all evals pass.
Model and API base: `evals/promptfoo/provider.py` (`MODEL`, `API_BASE`).

## Structure

```
skills/
  engineering/    ← harness-audit, setup-harness-skills, context-handover,
                     session-start, harness-triage, harness-prd, harness-issues, harness-guide
  productivity/   ← write-harness-skill, skill-cleanup
evals/promptfoo/  ← one <skill>.yaml per skill (canonical eval definition)
.claude-plugin/plugin.json  ← registered skill list
```

Root `SKILL.md` absent by design — `npx skills` discovers from bucket subfolders.
Each skill needs an entry in top-level `README.md` and `.claude-plugin/plugin.json`.

## Conventions

- Skill content: `SKILL.md` + `references/*.md`. Canonical evals: `evals/promptfoo/<skill>.yaml`.
- No snippet duplication — stack-specific content in `node-snippets.md`/`python-snippets.md`, not `universal-snippets.md`.
- Every gate in `SKILL.md` must name its failure mode (one sentence). No failure mode = don't add it.
- New eval scenario → add to `evals/promptfoo/<skill>.yaml` first, then update `SKILL.md`.
- KISS / YAGNI / DRY. When two solutions close the same gap, prefer fewer moving parts.

## Invariants (harness-audit skill)

- **Stop hook is always gap #1** when `.claude/settings.json` is missing — no other gap may precede it.
- **AGENTS.md ≡ CLAUDE.md** — never flag missing CLAUDE.md when AGENTS.md is present; never recommend creating both.
- **Brownfield**: recommend `eslint --fix` in a single cleanup commit, never manual fix-all.
- Multi-day scope output must name at least one anti-pattern (Fuzzy Done / Proxy Signal / Confidence Exit) and include a Judge audit as exit criterion.
- Snippets must be complete and paste-ready — no `YOUR_PROJECT_NAME` placeholders.
