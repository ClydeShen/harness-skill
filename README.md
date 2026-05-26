# harness-engineering-skill

A curated 13-skill collection for compound engineering workflows, packaged as a Claude Code / Codex plugin.

## What's included

### Engineering skills (`skills/engineering/`)

| Skill | Purpose |
|---|---|
| `harness-engineering` | Detect agent-harness gaps; output paste-ready fix snippets |
| `setup-harness-skills` | One-time gateway: configure GitHub, labels, `.planning/` state |
| `context-handover` | End-of-context-window session transition |
| `session-start` | Phase detection, interrupted-session recovery, session briefing |
| `triage` | Issue triage state machine |
| `to-prd` | Convert conversation to PRD with technical constraints |
| `to-issues` | Break PRD into vertical-slice user stories |
| `zoom-out` | Gain high-level architectural perspective |
| `grill-with-docs` | Interview relentlessly against reference docs until shared understanding is reached |

### Productivity skills (`skills/productivity/`)

| Skill | Purpose |
|---|---|
| `caveman` | Explain complex topics in plain language |
| `grill-me` | Stress-test a plan through relentless questioning |
| `handoff` | Hand off context to another agent or session |
| `write-a-skill` | Create a new skill with proper structure |

## Installation

### Quick install — `harness-engineering` skill only

```bash
npx skills add ClydeShen/harness-skill@harness-engineering -g
```

Installs the `harness-engineering` skill globally and symlinks it into Claude Code, Codex, Kiro, Pi, and all other detected runtimes automatically.

### Full collection — all 13 skills

Add to `~/.claude/settings.json`:

```json
{
  "plugins": [
    { "type": "git", "url": "https://github.com/ClydeShen/harness-skill" }
  ]
}
```

Or symlink locally from a clone:

```bash
bash scripts/link-skills.sh
```

## Getting started

### After quick install (`harness-engineering` only)

Open Claude Code in your project and run:

```
/harness-engineering
```

Or just say: _"set up harness"_, _"what do I need before I start"_, _"session start"_

The skill runs in three phases:

1. **Detect** — scans your project for missing harness components (stop hook, CI, pre-commit, instruction file, memory system, etc.)
2. **Interview** — asks up to 3 questions to resolve what the file scan can't determine (task scope, team size, stack)
3. **Output** — produces a prioritised gap list with complete, paste-ready snippets for the top 5 gaps

Copy the snippets and paste them directly — no placeholders to fill in.

---

### After full install (all 13 skills)

The skills cover the full compound engineering lifecycle. A typical project flow:

| Step | Skill | When |
|---|---|---|
| 1 | `/harness-engineering` | First time in a project — detect and close gaps |
| 2 | `/setup-harness-skills` | One-time project setup: GitHub labels, branch protection, `.planning/` state |
| 3 | `/session-start` | Beginning of every work session |
| 4 | `/to-prd` → `/to-issues` | Plan phase: turn a conversation into a PRD, then into GitHub issues |
| 5 | `/triage` | Ongoing: classify and route incoming issues |
| 6 | `/context-handover` | End of every session (fires automatically near context limit) |

Skills trigger automatically from natural language — you rarely need to type the slash command explicitly.

## Skill structure

```
skills/
  engineering/
    harness-engineering/
      SKILL.md               ← detect → interview → output flow
      skill.json
      evals/evals.json
      references/
        detect.md            ← gap classification logic
        universal-snippets.md
        node-snippets.md
        python-snippets.md
        kiro-snippets.md
        scenarios.md
    setup-harness-skills/  context-handover/  session-start/
    triage/  to-prd/  to-issues/  zoom-out/  grill-with-docs/
  productivity/
    caveman/  grill-me/  handoff/  write-a-skill/
evals/
  run_evals.py               ← promptfoo runner (discovers all skill configs)
  promptfoo/
    <skill-name>.yaml        ← one promptfoo config per skill (13 total)
    provider.py              ← response provider: llamacpp HTTP at localhost:8080
    grader.py                ← judge provider: llamacpp HTTP at localhost:8080
    scaffold_helper.py       ← shared project scaffolding for eval fixtures
.claude-plugin/
  plugin.json                ← registered skill list
scripts/
  link-skills.sh             ← symlinks skills/ into ~/.claude/skills/
  list-skills.sh             ← lists all skills in collection
```

## Evals

Each skill has a dedicated promptfoo config in `evals/promptfoo/<skill-name>.yaml`.

```bash
# All skills:
python evals/run_evals.py

# One skill only:
python evals/run_evals.py --skill harness-engineering

# Filter to specific evals (regex against description):
python evals/run_evals.py --skill harness-engineering --filter "#2"

# Run promptfoo directly:
cd evals/promptfoo && promptfoo eval --config harness-engineering.yaml
```

Requires `promptfoo` on PATH and a llamacpp server at `localhost:8080`.

Before committing any change to a skill file, run the relevant eval and confirm all tests pass.
