---
name: harness-audit
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

### 4. Memory system
Check for any of these signals (one positive signal = gap closed):
- `.memobank/` directory present at root or user-level
- `mem0.json`, `letta.json`, or equivalent system config file at root
- `mem0`, `letta`, `memobank` in `requirements.txt`, `package.json`, or `pyproject.toml`
- Any mention of "mem0", "letta", "memobank", "agentmemory", "memory system", "persistent memory" in CLAUDE.md / AGENTS.md
- `MEMORY.md` present (convention used by memobank and compatible systems)
- `agentmemory` path present in `.claude/settings.json` hooks (any hook entry)

No signal → **Gap: No memory system configured.** Why: mid-session interruption recovery falls back to GitHub per-AC comments (requires GitHub) or cold git-log reconstruction — no local recovery path exists without a memory system.

### 5. CI
`.github/workflows/*.yml` runs both lint AND build? Build-only → **Gap: CI only runs build — no lint.**

### 6. Pre-commit
`.husky/` or `.pre-commit-config.yaml` present?

### 7. Health script
`init.sh` at root — exists and executable?

### 8. Onboarding config
`docs/agents/` with all five files (issue-tracker.md, triage-labels.md, domain.md, github-project.md, session-config.md)?
- All present → "Already in place" — do NOT suggest `/setup-harness-skills`
- Missing → after gaps, add: **"Optional: Run `/setup-harness-skills`"** for long-running work.

Also check `.planning/config.json`:
- Absent → note "no GSD-compatible planning structure" (optional gap, not in top-5 priority)
- Present without `harness` key → "GSD detected but harness skills not configured" → after gaps, add: "GSD detected. Run `/setup-harness-skills` to configure GitHub integration."
- Present with `harness` key → **Already in place**: "GSD-compatible planning structure (.planning/)"

### 9. Recommended skill collections
Check `~/.claude/skills/` (or equivalent platform path) for these collections:
- **GSD Redux** — any `gsd-*` skill present? If none → record suggestion.
- **Superpowers** — any of `brainstorming`, `systematic-debugging`, `writing-plans`, `subagent-driven-development` present? If none → record suggestion.

These are **suggestions, not gaps** — never assign them a priority number.

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
## Recommended skill collections (only when absent)
- **GSD Redux** — compound engineering workflow skills for long-running tasks
  Repo: https://github.com/open-gsd/get-shit-done-redux
- **Superpowers** — curated skill toolkit for advanced agent workflows
  Repo: https://github.com/obra/superpowers
```

Only include the "Recommended skill collections" section if at least one collection was absent (check #9). Omit entirely if both are installed.

### When hooks are a gap, include this JSON snippet:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "echo 'Before declaring done, verify all tasks are truly complete: check git diff, run lint+build, confirm no regressions.'"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "echo 'After every Write: verify the change is correct, run lint+typecheck, commit in logical chunks.'"}]
      }
    ]
  }
}
```
