# Architecture
_Generated: 2026-05-27_

## Overview

This repo is a curated collection of 15 Claude Code / Codex agent skills packaged as a plugin, covering compound engineering workflows from project setup and harness auditing through session management, issue lifecycle, and continuous coaching. Skills are plain-text LLM instruction files (SKILL.md) invoked by Claude Code at `/skill-name`; an eval harness validates each skill's observable outputs via a local llamacpp LLM server.

## Main Components

### Skill Plugin Layer
- **Responsibility:** Delivers callable agent behaviours to Claude Code / Codex / Kiro / Gemini.
- **Registry:** `.claude-plugin/plugin.json` — lists all 15 skill paths; version `2.4.0`.
- **Install mechanism:** `scripts/link-skills.sh` symlinks every `skills/*/*/` directory into `~/.claude/skills/`.
- **Key files:**
  - `.claude-plugin/plugin.json` — canonical skill registry
  - `scripts/link-skills.sh` — installation script
  - `scripts/list-skills.sh` — lists all registered skills

### Skill Definition Units
Each skill is a self-contained directory. The minimum required file is `SKILL.md`.

Structure for a full skill:
```
skills/<bucket>/<skill-name>/
├── SKILL.md         ← YAML frontmatter (name, description, arg hints) + LLM instructions
├── skill.json       ← npm-style metadata (name, version, author, tags) — present on some skills
├── evals/
│   └── evals.json   ← legacy acceptance criteria (still present, superseded)
└── references/
    └── *.md         ← supplementary reference files injected as system-prompt context
```

The `description` field in the SKILL.md frontmatter is the **only text the agent sees** when deciding which skill to load. It must be ≤1024 chars and follow the "What it does. Use when [triggers]." format.

**Engineering skills** (`skills/engineering/`):
| Skill | Key file | Phase |
|---|---|---|
| `harness-audit` | `skills/engineering/harness-audit/SKILL.md` | Any — gap detection |
| `setup-harness-skills` | `skills/engineering/setup-harness-skills/SKILL.md` | Onboarding |
| `context-handover` | `skills/engineering/context-handover/SKILL.md` | End-of-session |
| `session-start` | `skills/engineering/session-start/SKILL.md` | Start-of-session |
| `triage` | `skills/engineering/triage/SKILL.md` | Issue management |
| `to-prd` | `skills/engineering/to-prd/SKILL.md` | Planning |
| `to-issues` | `skills/engineering/to-issues/SKILL.md` | Planning |
| `zoom-out` | `skills/engineering/zoom-out/SKILL.md` | Execution |
| `grill-with-docs` | `skills/engineering/grill-with-docs/SKILL.md` | Any |
| `harness-guide` | `skills/engineering/harness-guide/SKILL.md` | Any — coaching |

**Productivity skills** (`skills/productivity/`):
| Skill | Key file |
|---|---|
| `caveman` | `skills/productivity/caveman/SKILL.md` |
| `grill-me` | `skills/productivity/grill-me/SKILL.md` |
| `handoff` | `skills/productivity/handoff/SKILL.md` |
| `write-a-skill` | `skills/productivity/write-a-skill/SKILL.md` |
| `skill-cleanup` | `skills/productivity/skill-cleanup/SKILL.md` |

### Eval Harness
- **Responsibility:** Validates skill behaviour against an LLM judge running on a local llamacpp server at `localhost:8080`.
- **Runner:** `evals/run_evals.py` — discovers all `evals/promptfoo/*.yaml` configs and executes them via `promptfoo eval`.
- **Per-skill configs:** `evals/promptfoo/<skill-name>.yaml` — canonical eval definitions (5 skills currently have promptfoo configs; legacy `evals/evals.json` files exist for all skills).
- **Provider:** `evals/promptfoo/provider.py` — resolves skill directory, loads SKILL.md + all `references/*.md` as the system prompt, scaffolds a temporary project directory, calls llamacpp HTTP for the model response.
- **Grader:** `evals/promptfoo/grader.py` — LLM judge; receives promptfoo's rubric prompt and returns `{"pass": bool, "score": float, "reason": str}`.
- **Scaffold helper:** `evals/promptfoo/scaffold_helper.py` — interprets plain-English `scaffold_files` hints from YAML test vars into realistic filesystem trees in a temp directory.

## Data Flow

### Skill Invocation (runtime)
```
User types /skill-name [optional context]
     │
     ▼
Claude Code reads ~/.claude/skills/<skill-name>/SKILL.md
     │  (description in frontmatter was used to route here)
     ▼
SKILL.md content + any referenced files injected as system context
     │
     ▼
Agent executes skill phases (Detect → Interview → Output, or
                              Inspect → Classify → Recommend, etc.)
     │
     ▼
Agent reads/writes project files (.harness/, .claude/, docs/agents/, GitHub)
```

### Eval Execution
```
python evals/run_evals.py [--skill NAME] [--filter DESC]
     │
     ▼
Discovers evals/promptfoo/<skill>.yaml
     │
     ▼
promptfoo eval → provider.py::call_api(prompt, options, context)
     │  - resolves skills/*/<skill>/SKILL.md + references/
     │  - loads system prompt (strips YAML frontmatter)
     │  - scaffold_helper.scaffold(tmpdir, scaffold_files)
     │  - builds file listing of temp project
     │  - POST localhost:8080/v1/chat/completions
     │
     ▼
Model response (string)
     │
     ▼
promptfoo asserts: icontains / not-icontains / llm-rubric
     │  llm-rubric → grader.py::call_api(rubric_prompt)
     │    - POST localhost:8080/v1/chat/completions (judge model)
     │    - returns {"pass": bool, "score": float, "reason": str}
     │
     ▼
Pass/fail verdict per assertion → evals/promptfoo/output-<skill>.json
```

### Session State Flow (cross-session continuity)
```
/setup-harness-skills
     │ writes .harness/config.json, STATE.md, PROJECT.md, ROADMAP.md
     ▼
/session-start (start of session)
     │ reads STATE.md → detects session_status (idle / in_progress / interrupted)
     │ reads .harness/phases/<phase>/.continue-here.md
     │ sets session_status: in_progress
     ▼
Work: /triage, /to-prd, /to-issues, /harness-guide, etc.
     │ reads/writes .harness/, docs/agents/, GitHub issues
     ▼
/context-handover (≥70–80% context used)
     │ invokes memory system
     │ writes .harness/phases/<phase>/.continue-here.md
     │ sets STATE.md session_status: idle
     │ posts GitHub progress comment (if docs/agents/ configured)
     ▼
/session-start (next session)
```

## Key Patterns

### Three-Phase Skill Structure (harness-audit, harness-guide)
Skills with detection logic follow a strict three-phase pattern defined in SKILL.md:
1. **Detect/Inspect** — read files silently, build complete gap list before any output
2. **Interview/Classify** — ask at most 3 questions one at a time; classify into buckets
3. **Output/Recommend** — produce prioritised list with paste-ready snippets; exactly one recommendation at a time

### Invariant Ordering
Stop hook is always gap #1 when `.claude/settings.json` is absent — no other gap may precede it. This invariant is tested in eval #10 (`harness-audit.yaml`) and enforced in `harness-guide/SKILL.md`.

### Progressive Disclosure via Reference Files
Skills split content across `SKILL.md` (primary, always loaded) and `references/*.md` (supplementary, injected by `provider.py` during evals). Stack-specific snippets (`node-snippets.md`, `python-snippets.md`, `kiro-snippets.md`) are never duplicated in `universal-snippets.md`.

### Failure-Mode Justification
Every gate recommendation in SKILL.md must state a one-sentence failure mode. No failure mode = gate is not added. This is enforced as an editing convention in `CLAUDE.md`.

### Vertical Slice Issue Decomposition (to-issues)
Issues are decomposed as tracer-bullet vertical slices — each slice cuts through ALL integration layers end-to-end and must be independently demoable. Three creation gates enforced: (1) Estimable, (2) ≤8 context windows, (3) demoable user-facing outcome.

### Token-Budget Units
All effort sizing uses "context windows" as the unit (1 ≈ 30K–60K tokens). This unit appears in triage agent briefs, PLAN.md task blocks, `to-issues` effort estimates, and the `context-handover` GitHub comment.

### Agent-Runtime Equivalences
`AGENTS.md` is fully equivalent to `CLAUDE.md` — never flag one as missing when the other is present. Kiro `.kiro/hooks/agentTurnEnd` is equivalent to the Claude Stop hook. `GEMINI.md` is the Gemini instruction file equivalent.

### Memory System Abstraction
The memory system is treated as a black box. Any of `memobank`, `mem0`, `letta`, `MEMORY.md`, or equivalent system config constitutes a satisfied memory gap. `context-handover` triggers the active system without caring which one it is.

## Entry Points

**Skill invocation (Claude Code):**
- Any `SKILL.md` under `~/.claude/skills/` — invoked with `/skill-name`

**Eval entry point:**
- `evals/run_evals.py` — CLI runner for all or a single skill

**Installation:**
- `scripts/link-skills.sh` — symlinks skills into `~/.claude/skills/`

**Plugin registration:**
- `.claude-plugin/plugin.json` — consumed by `npx skills` discovery

**Session state bootstrap:**
- `skills/engineering/setup-harness-skills/SKILL.md` — first-run setup; writes `.harness/config.json`, `STATE.md`, `PROJECT.md`, `ROADMAP.md`, `docs/agents/`

## Anti-Patterns

### Batch Questioning
**What happens:** Skill asks multiple questions in one message.
**Why it's wrong:** User cognitive load spikes; agent loses track of which answer addresses which question.
**Do this instead:** One question at a time; wait for answer before next question (enforced in `harness-guide/SKILL.md` and `setup-harness-skills/SKILL.md`).

### Planning=Done
**What happens:** A commit named "add plan" with no subsequent build/verify commit is treated as task completion.
**Why it's wrong:** The feature is not built; user believes work is complete.
**Defined in:** `skills/engineering/harness-guide/references/anti-patterns.md`

### Proxy Signal
**What happens:** CI passes (build only, no lint/test) and is treated as proof the feature works.
**Why it's wrong:** The proxy measure is satisfied while actual requirement is not verified.
**Defined in:** `skills/engineering/harness-guide/references/anti-patterns.md`

## Error Handling

**Eval provider:** Returns `{"error": str}` on connection failure or exception; never raises. Graceful degradation for missing skill directories (`FileNotFoundError` caught and returned as error dict).

**Eval grader:** Retries up to 3 times on non-parseable verdicts; falls back to keyword matching (`PASS`/`FAIL` in response) before returning a forced-fail verdict.

**Skills:** Graceful degradation tables in `context-handover/SKILL.md` and `session-start/SKILL.md` specify fallback behaviour for each missing artifact (no `.harness/`, no `docs/agents/`, no memory system, no GitHub remote).
