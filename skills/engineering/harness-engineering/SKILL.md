---
name: harness-engineering
description: Scans a project for agent-harness gaps and outputs a prioritised list with paste-ready config snippets to close them. Covers hooks, CI, pre-commit, instruction file quality, init.sh, and session discipline. Use when starting a new project, auditing an existing harness, writing or reviewing CLAUDE.md/AGENTS.md, setting up CI gates, beginning multi-day autonomous work, or when user says "set up harness", "health check", "agent discipline", "project setup", "pre-commit hooks", "stop hook", "verification gap".
---

# Harness Engineering — Gap Analysis

**You are a gap analysis tool. Never create files, run git, or say "Harness is set up" or "Done".**

---

## Detection Checklist

Check each item. List unsatisfied items as gaps in priority order.

### 0. Pre-task checklist (for tasks >30 min)
Before analyzing gaps, state: **"run lint + build to verify the baseline, check git status, read the relevant spec, Initial Interview with Sprint Contract."**

### 1. Stop hook
`.claude/settings.json` absent or no `Stop` entry? → **Gap: Missing Stop hook.** (Highest priority — nothing precedes it.)

### 2. PostToolUse hook
`.claude/settings.json` absent or no `PostToolUse` entry? → **Gap: Missing PostToolUse hook.** Separate from Stop hook.

### 3. Instruction file
`CLAUDE.md` or `AGENTS.md` present? (Fully equivalent — one is sufficient.)
- If neither → **Gap: No agent instruction file.**
- If present and >200 lines → **Gap: Instruction file exceeds 200-line ceiling.**
- **If AGENTS.md is present (user mentions AGENTS.md or asks about CLAUDE.md):**  
  You MUST state: **"AGENTS.md is the instruction file — it is equivalent to CLAUDE.md, you do not need a CLAUDE.md."**  
  Then comment on its quality (line count vs 200 ceiling). Then identify OTHER gaps.

### 4. CI
`.github/workflows/*.yml` runs both lint AND build? Build-only → **Gap: CI only runs build — no lint.**

### 5. Pre-commit
`.husky/` or `.pre-commit-config.yaml` present?

### 6. Health script
`init.sh` at root — exists and executable?

### 7. Onboarding config
`docs/agents/` with all five files (issue-tracker.md, triage-labels.md, domain.md, github-project.md, session-config.md)?
- All present → "Already in place" — do NOT suggest `/setup-harness-skills`
- Missing → after gaps, add: **"Optional: Run `/setup-harness-skills`"** for long-running work.

---

## Runtime-Specific

**Kiro** (`.kiro/` detected or user mentions Kiro):  
You MUST include the word **"Kiro"** in your response.  
Add after gaps: `".kiro/hooks/ with agentTurnEnd replaces Stop hook; postToolUse replaces PostToolUse. .kiro/steering/ replaces CLAUDE.md."`

**Gemini** (`.gemini/` detected or user mentions Gemini):  
You MUST include **"GEMINI.md"** as the instruction file name.  
Add after gaps: `"GEMINI.md is the instruction file (same 200-line ceiling). Hook equivalents are not publicly documented — verify in your Gemini agent's settings."`

**Brownfield** (existing lint errors):  
State **"This is a brownfield codebase."** Recommend `eslint --fix .` in one cleanup commit. Pre-commit catches new violations only. Never require manual fixes.

---

## Multi-Day Tasks (week+)

For long autonomous work, include ALL of these phrases:
- **"one active task at a time"**
- **"Fuzzy Done"** or **"Proxy Signal"** or **"Confidence Exit"** or **"Planning=Done"**
- **"Judge audit"** — as the exit criterion
- **"observable behavior"** as completion proof
- **Session handoff** strategy

---

## Output Format

```
## Already in place
## Harness gaps (priority order)
### 1. Missing Stop hook
**Why it matters:** [one sentence]
**Fix:** [paste-ready snippet]
### 2. [Next gap]
**Why it matters:** [one sentence]
**Fix:** [paste-ready snippet]
## What to do next
```

### When hooks are a gap, include this JSON snippet:
```json
{
  "hooks": {
    "Stop": [{"prompt": "Before declaring done, verify all tasks are truly complete: check git diff, run lint+build, confirm no regressions."}],
    "PostToolUse": [{"matcher": {"type": "Write"}, "hooks": [{"prompt": "After every Write: verify the change is correct, run lint+typecheck, commit in logical chunks."}]}]
  }
}
```
