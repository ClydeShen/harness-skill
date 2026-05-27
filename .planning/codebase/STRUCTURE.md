# Structure
_Generated: 2026-05-27_

## Directory Layout

```
harness-engineering-skill/
├── skills/                        # All agent skill definitions
│   ├── engineering/               # Daily code-work skills (10 skills)
│   │   ├── harness-audit/         # Gap detection + paste-ready fix snippets
│   │   │   ├── SKILL.md           # Primary instructions (frontmatter + content)
│   │   │   ├── skill.json         # npm-style metadata (name, version, author, tags)
│   │   │   ├── evals/evals.json   # Legacy acceptance criteria
│   │   │   └── references/        # Supplementary context injected during evals
│   │   │       ├── universal-snippets.md
│   │   │       ├── node-snippets.md
│   │   │       ├── python-snippets.md
│   │   │       ├── kiro-snippets.md
│   │   │       ├── detect.md
│   │   │       ├── scenarios.md
│   │   │       └── recommended-skills.md
│   │   ├── harness-guide/         # Continuous coaching toward best practices
│   │   │   ├── SKILL.md
│   │   │   ├── skill.json
│   │   │   └── references/
│   │   │       ├── anti-patterns.md   # Named anti-patterns with signals + failure modes
│   │   │       └── best-practices.md
│   │   ├── setup-harness-skills/  # One-time project harness setup
│   │   │   ├── SKILL.md
│   │   │   ├── output-steps.md    # 10-step post-interview output sequence
│   │   │   ├── session-config.md
│   │   │   ├── triage-labels.md
│   │   │   ├── domain.md
│   │   │   ├── github-project.md
│   │   │   ├── issue-tracker-github.md
│   │   │   ├── issue-tracker-github-projects.md
│   │   │   └── evals/evals.json
│   │   ├── context-handover/      # End-of-context-window session transition
│   │   │   ├── SKILL.md
│   │   │   ├── phase-budgets.md   # Per-phase session budget tables (shared with session-start)
│   │   │   └── evals/evals.json
│   │   ├── session-start/         # Resume from .planning/STATE.md
│   │   │   ├── SKILL.md
│   │   │   └── evals/evals.json
│   │   ├── triage/                # Issue triage state machine
│   │   │   ├── SKILL.md
│   │   │   ├── AGENT-BRIEF.md     # Agent brief format guidance
│   │   │   ├── OUT-OF-SCOPE.md    # .out-of-scope/ knowledge base spec
│   │   │   ├── references/
│   │   │   │   └── effort-calibration.md  # Token-budget sizing table
│   │   │   └── evals/evals.json
│   │   ├── to-prd/                # Conversation → PRD → issue tracker
│   │   │   ├── SKILL.md
│   │   │   └── evals/evals.json
│   │   ├── to-issues/             # PRD → vertical-slice issues
│   │   │   ├── SKILL.md
│   │   │   └── evals/evals.json
│   │   ├── zoom-out/              # Architectural map / module caller context
│   │   │   ├── SKILL.md
│   │   │   └── evals/evals.json
│   │   └── grill-with-docs/       # Relentless interview against docs/ADRs
│   │       ├── SKILL.md
│   │       ├── ADR-FORMAT.md
│   │       ├── CONTEXT-FORMAT.md
│   │       └── evals/evals.json
│   ├── productivity/              # Non-code workflow tools (5 skills)
│   │   ├── caveman/               # First-principles simplification
│   │   ├── grill-me/              # Interview-style plan stress-test
│   │   ├── handoff/               # Lightweight subagent briefing
│   │   ├── write-a-skill/         # Create new skills with proper structure
│   │   └── skill-cleanup/         # Interactive skill maintenance (has node_modules)
│   ├── engineering/README.md      # Skill index with source attribution
│   └── productivity/README.md     # Skill index
│
├── evals/                         # Eval harness
│   ├── run_evals.py               # CLI runner: discovers configs, invokes promptfoo
│   └── promptfoo/
│       ├── provider.py            # Response provider: llamacpp HTTP at localhost:8080
│       ├── grader.py              # LLM judge provider: llamacpp HTTP at localhost:8080
│       ├── scaffold_helper.py     # Plain-English → filesystem scaffold for test vars
│       ├── provider_pi.py         # Alternative pi-CLI provider (reference only)
│       ├── harness-audit.yaml     # Canonical eval config — 16 scenarios
│       ├── harness-guide.yaml     # Canonical eval config
│       ├── context-handover.yaml  # Canonical eval config
│       ├── session-start.yaml     # Canonical eval config
│       └── setup-harness-skills.yaml  # Canonical eval config
│
├── .claude-plugin/
│   ├── plugin.json                # Skill registry consumed by npx skills
│   └── link-skills.sh             # Duplicate of scripts/link-skills.sh
│
├── scripts/
│   ├── link-skills.sh             # Symlinks skills/ into ~/.claude/skills/
│   └── list-skills.sh             # Lists all skills in collection
│
├── docs/
│   ├── adr/                       # Architecture Decision Records
│   ├── agents/                    # Harness skill runtime config (GSD format)
│   ├── goals/                     # Project goals and eval-verification notes
│   └── superpowers/               # Plans and specs
│
├── .planning/                     # GSD-compatible session state
│   ├── config.json                # GSD config + harness namespace
│   ├── STATE.md                   # Active phase, session_status, continuity
│   ├── PROJECT.md                 # Project context
│   ├── ROADMAP.md                 # Phase entries (01-discuss → 04-verify)
│   ├── codebase/                  # Codebase map documents (this file)
│   └── phases/                    # Per-phase artifacts
│       └── 01-discuss/
│
├── .claude/                       # Claude Code runtime config
│   └── settings.json              # Stop hook + PostToolUse hook definitions
│
├── .github/
│   └── workflows/                 # CI pipeline definitions
│
├── .memobank/                     # Persistent memory system (memobank)
├── CLAUDE.md                      # Agent instruction file (200-line ceiling)
└── README.md                      # Top-level index (links each skill to SKILL.md)
```

## Module Responsibilities

### `skills/engineering/harness-audit/`
Detects agent-harness gaps (Stop hook, PostToolUse hook, instruction file, memory system, CI, pre-commit, health script, onboarding config, skill collections). Outputs a prioritised gap list with paste-ready config snippets. The `references/` subdirectory is loaded as additional system-prompt context during evals; snippets are stack-segregated across `node-snippets.md`, `python-snippets.md`, `kiro-snippets.md`, and `universal-snippets.md`.

### `skills/engineering/harness-guide/`
Continuous coaching loop: Inspect → Classify (aligned / weak / missing) → Recommend one next step. References `references/anti-patterns.md` by name when classifying weak patterns.

### `skills/engineering/setup-harness-skills/`
One-time onboarding gateway. Explores existing project state before asking questions, then walks through five sections (issue tracker, instruction file, labels, domain docs, GitHub board) one at a time. Writes `.planning/config.json`, `STATE.md`, `PROJECT.md`, `ROADMAP.md`, `docs/agents/` seed files, and the `## Agent skills` block in CLAUDE.md/AGENTS.md. Output sequence is delegated to `output-steps.md`.

### `skills/engineering/context-handover/` + `skills/engineering/session-start/`
Together they implement the session state machine. `context-handover` transitions `session_status: in_progress → idle` and writes `.continue-here.md`. `session-start` reads `STATE.md`, transitions `idle → in_progress`, and detects interrupted sessions (stale `in_progress` timestamp). Phase budget tables shared via `context-handover/phase-budgets.md`.

### `skills/engineering/triage/`
Issue state-machine driver. Moves issues through: unlabeled → needs-triage → (needs-info | ready-for-agent | ready-for-human | wontfix). Posts AI-generated comments with disclaimer. Agent-brief format defined in `AGENT-BRIEF.md`; out-of-scope knowledge base in `OUT-OF-SCOPE.md`.

### `skills/engineering/to-prd/` + `skills/engineering/to-issues/`
Planning pipeline. `to-prd` synthesises conversation context into a PRD (issue tracker or GSD CONTEXT.md format). `to-issues` breaks a PRD into tracer-bullet vertical-slice issues, enforcing three creation gates (estimable, ≤8 context windows, demoable). Both also write GSD-format local files (`.planning/phases/01-discuss/01-CONTEXT.md`, `.planning/phases/02-plan/02-PLAN.md`).

### `skills/productivity/write-a-skill/`
Documents the conventions for creating new skills: SKILL.md structure, description requirements (≤1024 chars, trigger phrases), when to add `references/` files, and a review checklist including the AI-generated footer requirement.

### `evals/run_evals.py`
CLI orchestrator. Discovers `evals/promptfoo/*.yaml` configs (excluding `output-*.yaml`), runs each via `promptfoo eval --no-cache`, and exits non-zero if any fail.

### `evals/promptfoo/provider.py`
Eval response provider. Resolves `skills/*/<skill_name>/` via glob, loads SKILL.md + `references/*.md` into a cached system prompt, calls `scaffold_helper.scaffold()` to create a realistic temp project, then calls the llamacpp HTTP endpoint. Model: `qwen2.5-coder-32b-instruct-q5_k_m.gguf`.

### `evals/promptfoo/grader.py`
LLM judge. Receives promptfoo's rubric prompt, returns a JSON verdict. Handles Qwen3 `<think>` preambles via bracket-matching JSON extraction. Retries up to 3 times. Judge model: `Qwen3.6-35B-A3B-UD-Q5_K_M.gguf`.

### `evals/promptfoo/scaffold_helper.py`
Interprets plain-English `scaffold_files` hints from YAML test vars into real filesystem trees. Handles: `package.json`, `tsconfig.json`, `.github/workflows/ci.yml` (with/without lint), `CLAUDE.md` (various line counts), `AGENTS.md`, `.claude/settings.json` (Stop+PostToolUse or PostToolUse-only), `.planning/STATE.md` (idle/interrupted), `.planning/phases/<phase>/.continue-here.md`, `.planning/config.json` (with/without harness key), `.git/config` (with remote origin), `docs/agents/` seed files, `.kiro/`, `.gemini/`, and more.

## Naming Conventions

### Files
- Skill instruction files: `SKILL.md` (UPPERCASE, always)
- Skill metadata: `skill.json` (lowercase)
- Legacy eval data: `evals/evals.json` (lowercase, plural)
- Canonical eval configs: `evals/promptfoo/<skill-name>.yaml` (kebab-case, matches skill name)
- Reference documents: `<descriptor>.md` inside `references/` (kebab-case, descriptive)
- Promptfoo output files: `output-<skill-name>.json` (excluded from eval discovery)
- Session continuity file: `.continue-here.md` (always this exact name)
- Session state: `STATE.md` (UPPERCASE)

### Directories
- Skill names: `kebab-case` matching the invocation command (e.g., `harness-audit` → `/harness-audit`)
- Bucket names: `engineering/` or `productivity/` (lowercase, plural)
- Phase directories: `NN-name/` with two-digit prefix (e.g., `01-discuss`, `02-plan`, `03-execute`, `04-verify`)

### SKILL.md Frontmatter Fields
- `name`: kebab-case, matches directory name
- `description`: ≤1024 chars; "What it does. Use when [specific triggers]."
- `argument-hint`: optional, shown in agent UI
- `disable-model-invocation: true`: on skills that are pure instruction macros with no LLM output (e.g., `zoom-out`)

## Where to Add New Code

### New engineering skill
1. Create `skills/engineering/<skill-name>/SKILL.md` with YAML frontmatter and LLM instructions
2. Add `skills/engineering/<skill-name>/skill.json` with name, version, author, tags
3. Create `skills/engineering/<skill-name>/evals/evals.json` with acceptance criteria
4. Add to `.claude-plugin/plugin.json` skills array
5. Add entry to `skills/engineering/README.md`
6. Add entry to top-level `README.md`
7. Create `evals/promptfoo/<skill-name>.yaml` (canonical eval — do this first before updating SKILL.md)
8. If SKILL.md exceeds 500 lines or has stack-specific content, extract to `skills/engineering/<skill-name>/references/`

### New productivity skill
Same as above but under `skills/productivity/` and `skills/productivity/README.md`.

### New eval scenario for an existing skill
1. Add test block to `evals/promptfoo/<skill-name>.yaml`
2. Update `SKILL.md` to cover the new scenario (YAML first, SKILL.md second — per CLAUDE.md)

### New scaffold type in evals
Add a new condition block to `evals/promptfoo/scaffold_helper.py::scaffold()` using the pattern: check `desc` string for plain-English hint, create files under `root /`.

### New reference file for a skill
Place in `skills/<bucket>/<skill-name>/references/<descriptor>.md`. Do NOT duplicate content present in `universal-snippets.md` — stack-specific content goes in stack-specific files only.
