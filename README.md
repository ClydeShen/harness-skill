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

### Claude Code (plugin)

Add to `~/.claude/settings.json`:

```json
{
  "plugins": [
    { "type": "git", "url": "https://github.com/ClydeShen/harness-skill" }
  ]
}
```

Or symlink the skills directory locally:

```bash
bash scripts/link-skills.sh
```

### Codex

Skills installed via the plugin are auto-discovered by Codex. No additional config needed.

## Usage

Skills trigger automatically from natural language or can be invoked explicitly:

```
/harness-engineering
/session-start
/context-handover
```

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
