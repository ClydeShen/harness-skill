# Harness Anti-Patterns

Anti-patterns detected during Phase 2 — Classify. Each entry names the pattern, describes the signal, and states the failure mode.

---

## Planning=Done

**Signal:** Task committed as "plan X" or "outline feature Y" with no subsequent build, test, or verify commit. STATE.md shows phase advancing without observable output.

**Failure mode:** The agent treats a written plan as a deliverable. The feature is not built. The user believes work is complete; it is not.

**Detection:** `git log --oneline` shows planning commits without corresponding implementation or verification commits on the same task.

---

## Fuzzy Done

**Signal:** Agent declares a task complete based on ambiguous markers — "I think this is working", "looks correct to me", "should be fine" — without running tests, lint, or build verification.

**Failure mode:** Unverified completion cascades into the next task. Regressions accumulate silently. The first real signal is a failing CI run or user-reported bug.

**Detection:** Task closure in STATE.md or git with no lint/build/test command in the same session. No verification commit before `session_status: idle`.

---

## Proxy Signal

**Signal:** A passing CI build is treated as proof the feature works. Or: "no TypeScript errors" is used to confirm business logic correctness.

**Failure mode:** The proxy measure (build pass, type check) is satisfied while the actual requirement (feature behavior, user workflow) is not verified. Defects ship.

**Detection:** CI config runs `npm run build` only — no lint step, no test step. Or: evaluation coverage exists for syntax but not for observable output.

---

## Confidence Exit

**Signal:** Agent skips verification steps because it is confident in the outcome. "I'm sure this is correct." "No need to run tests — the logic is straightforward."

**Failure mode:** Confidence is not a test. Non-obvious edge cases, integration failures, and environment differences are invisible to confidence assessments.

**Detection:** Git log shows task commits without a verification commit. No lint/build command in session context before done declaration.

---

## Context Drift

**Signal:** Mid-session commits diverge from the original task description. Refactors appear during a bug fix. New features appear during a refactor. The final commit doesn't map to the issue.

**Failure mode:** Original task is not completed. Side work introduces new bugs. Reviewer cannot match diff to requirement.

**Detection:** Git commit messages on a single task branch span unrelated modules or concerns. Issue acceptance criteria are not all addressed by the commit set.

---

## Scope Creep

**Signal:** Task scope expands beyond what was specified — surrounding code is refactored, unrelated features are added, or improvements are made to files not mentioned in the issue.

**Failure mode:** Review surface grows. Risk surface grows. Session context is consumed on work that wasn't requested. Related issues are invalidated by unexpected changes.

**Detection:** Diff includes modifications to files outside the task's stated scope. Commit message says "also cleaned up X" or "while I was there".

---

## Batch Questioning

**Signal:** Agent asks two or more questions in a single message — "What's your timeline? Also, which database? And should I use TypeScript?"

**Failure mode:** User cognitive load spikes. Answers become interleaved. The agent loses track of which answer addresses which question. Subsequent questions are asked without waiting for the first answer.

**Detection:** Any message containing more than one question mark directed at the user, where each question is distinct and not part of a clarifying sub-clause.
