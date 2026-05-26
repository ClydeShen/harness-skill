# Harness Engineering Skills

[![skills.sh](https://skills.sh/b/ClydeShen/harness-skill)](https://skills.sh/ClydeShen/harness-skill)

Agent skills for compound engineering workflows — structured sessions, context handover, issue lifecycle, and harness health.

## Quickstart

```bash
npx skills add ClydeShen/harness-skill@harness-audit -g
```

This installs `harness-audit` into Claude Code, Codex, Kiro, Pi, and every other detected runtime automatically.

Then open your project in Claude Code and run:

```
/harness-audit
```

It scans for missing harness components, asks up to 3 questions, and outputs a prioritised gap list with paste-ready snippets.

## Full Collection (all 13 skills)

Add to `~/.claude/settings.json`:

```json
{
  "plugins": [
    { "type": "git", "url": "https://github.com/ClydeShen/harness-skill" }
  ]
}
```

Or clone and symlink locally:

```bash
bash scripts/link-skills.sh
```

## Reference

### Engineering

Skills for the full compound engineering lifecycle.

- **[harness-audit](./skills/engineering/harness-audit/SKILL.md)** — Detect agent-harness gaps and output paste-ready fix snippets. Run first in any new project.
- **[setup-harness-skills](./skills/engineering/setup-harness-skills/SKILL.md)** — One-time project setup: GitHub labels, branch protection, `.planning/` state structure.
- **[session-start](./skills/engineering/session-start/SKILL.md)** — Phase detection, interrupted-session recovery, and session briefing. Run at the start of every work session.
- **[context-handover](./skills/engineering/context-handover/SKILL.md)** — End-of-context-window session transition. Fires near context limit; preserves state across sessions.
- **[to-prd](./skills/engineering/to-prd/SKILL.md)** — Turn a conversation into a PRD with technical constraints and a spike recommendation.
- **[to-issues](./skills/engineering/to-issues/SKILL.md)** — Break a PRD into vertical-slice GitHub issues with AFK/HITL confidence labels.
- **[triage](./skills/engineering/triage/SKILL.md)** — Issue triage state machine: classify, label, and route incoming issues.
- **[grill-with-docs](./skills/engineering/grill-with-docs/SKILL.md)** — Interview relentlessly against reference docs until shared understanding is reached; updates `CONTEXT.md` and ADRs inline.
- **[zoom-out](./skills/engineering/zoom-out/SKILL.md)** — Tell the agent to zoom out and give a higher-level architectural perspective on an unfamiliar section of code.

### Productivity

General workflow tools, not code-specific.

- **[caveman](./skills/productivity/caveman/SKILL.md)** — Ultra-compressed communication mode. Cuts token usage by dropping filler while keeping full technical accuracy.
- **[grill-me](./skills/productivity/grill-me/SKILL.md)** — Relentless sequential interview that stress-tests a plan until every decision branch is resolved.
- **[handoff](./skills/productivity/handoff/SKILL.md)** — Compact the current conversation into a handoff document so another agent can continue the work.
- **[write-a-skill](./skills/productivity/write-a-skill/SKILL.md)** — Create new skills with proper structure, progressive disclosure, and bundled resources.
- **[skill-cleanup](./skills/productivity/skill-cleanup/SKILL.md)** — Scan installed skills, detect stale or renamed entries, and guide safe removal with confirmation.
