# Detection Guide

## Runtime Detection (Phase 1 Step 0)

Run this before all other checks. Presence of a runtime-specific directory
identifies which agent is executing the project.

| Directory present | Runtime | Full support? |
|---|---|---|
| `.claude/` | Claude Code / Codex | Yes — use `.claude/settings.json` snippets |
| `.kiro/` | Kiro | Yes — use `kiro-snippets.md` |
| `.gemini/` | Gemini | Best-effort — adapt Claude Code snippets; note Gemini equivalents |
| None of the above | Unknown | Consume Q2 slot to ask: "Which agent are you using?" |

> **Claude Desktop:** No code-editing harness to detect. Out of scope for gap
> analysis. If user mentions Claude Desktop, redirect to Claude Code docs.

> **Gemini best-effort:** Output Claude Code snippets for universal gaps (CI,
> init.sh). For hook gaps, note: "Gemini does not have a documented hook
> equivalent — verify in your Gemini agent's settings." For the instruction
> file gap, recommend `GEMINI.md` using the same structure as the CLAUDE.md
> template.

---

## Stack Detection

| File present | Stack |
|---|---|
| `package.json` with `typescript` dep or `tsconfig.json` | Node/TypeScript |
| `package.json` without TypeScript | Node/JavaScript |
| `pyproject.toml` or `requirements.txt` or `setup.py` | Python |
| `go.mod` | Go |
| None of the above | Unknown — ask |

If frontend: look for `next.config.*`, `vite.config.*`, `react` in deps.
Frontend detected → also check for `DESIGN.md`.

---

## Gap Classification

> **Note:** Claude Code reads both `CLAUDE.md` and `AGENTS.md` natively from the project root — they are equivalent. If either is present, the "agent instruction file" gap is closed. Apply all CLAUDE.md quality checks (line count, conditional tags, rules directory) to whichever file is present. Do NOT recommend creating `CLAUDE.md` when `AGENTS.md` already exists.

### Major gaps (each counts toward the Q3 threshold)

| Gap | Detection | Failure mode prevented |
|---|---|---|
| No Stop hook | Claude Code: `.claude/settings.json` missing or lacks `Stop` entry. Kiro: `.kiro/hooks/` missing or lacks `agentTurnEnd` hook | Agent declares done without verifying — most common failure mode |
| No PostToolUse hook | Claude Code: `.claude/settings.json` missing or lacks `PostToolUse` entry. Kiro: `.kiro/hooks/` missing or lacks `postToolUse` hook | Lint violations accumulate silently across edits |
| No agent instruction file | Claude Code/Codex: `CLAUDE.md` absent AND `AGENTS.md` absent. Kiro: `.kiro/steering/` absent or empty. Gemini: `GEMINI.md` absent | No persistent context anchor — every session starts blind |
| Agent instruction file over budget | `CLAUDE.md` or `AGENTS.md` exceeds 200 lines | Instructions degrade uniformly; critical rules get ignored |
| No CI | `.github/workflows/` absent or no lint+build steps | Broken code merges undetected |
| No health check | `init.sh` absent | Sessions start on a broken baseline without warning |

### Minor gaps (do not count toward Q3 threshold)

| Gap | Detection | Failure mode prevented |
|---|---|---|
| No pre-commit hooks | `.husky/` and `.pre-commit-config.yaml` both absent | Style violations reach commit; slow feedback loop |
| No spec workflow | `docs/superpowers/specs/` absent | Work starts without agreed done criteria |
| No DESIGN.md (frontend only) | `DESIGN.md` absent, frontend detected | UI work starts without visual language anchor |
| Instruction file has no `<important if>` tags or `.claude/rules/` | Scan file content and directory | Task-specific rules applied universally; foundational rules crowded out |
| No `.claude/rules/` when instruction file > 100 lines | `.claude/rules/` absent | Path-specific rules bloat the always-loaded context instead of loading on demand |
| Cross-session memory absent | None of the common memory signals detected (see below) | Preferences and decisions lost between sessions |
| No observability tooling | None of: `agentops` in deps, `agenttrace` installed, structured logging in entry-point files | Cost spikes, tool failures, and regressions go undetected across sessions |

---

## Detecting Cross-Session Memory

Count as "memory present" if **any** of these signals exist:

| Signal | Tool |
|---|---|
| `~/.claude/projects/*/memory/MEMORY.md` exists | Claude Code native auto memory |
| `MEMORY.md` in project root | Manual memory file (simple, zero-dep) |
| `.memobank/` directory in project root | memobank |
| `memory/` or `.memory/` directory in project root | Generic memory directory |
| `onecontext` in installed skills or CLAUDE.md reference | OneContext |
| `mem0` package in `package.json` / `pyproject.toml` | mem0 |
| `CLAUDE.md` references a memory file with `@` import | Custom memory via import |

If none found, suggest the simplest option first: a `MEMORY.md` file at project root with a note in `CLAUDE.md` to load it at session start. Only suggest heavier tools if the user asks.

---

## Interpreting CI workflows

A CI workflow counts as covering lint if it runs any of:
`eslint`, `ruff`, `golangci-lint`, `npm run lint`, `make lint`

A CI workflow counts as covering build if it runs any of:
`npm run build`, `next build`, `tsc --noEmit`, `go build`, `python -m build`, `make build`

If CI exists but covers neither, treat as "CI present but incomplete" — list as a gap with lower priority than "no CI".

---

## Interpreting .claude/settings.json

PostToolUse hook is present if `settings.json` contains a `PostToolUse` key
with a matcher covering `Edit` or `Write` and a non-empty `hooks` array.

Stop hook is present if `settings.json` contains a `Stop` key with a non-empty
`hooks` array containing a prompt entry.

If `settings.json` exists but hooks are missing or empty, treat as
"hooks configured but incomplete".

---

## Interpreting .kiro/hooks/

PostToolUse hook is present if `.kiro/hooks/` contains a JSON file with
`trigger.type` of `postToolUse` covering file-edit tools and `enabled: true`.

Stop hook is present if `.kiro/hooks/` contains a JSON file with
`trigger.type` of `agentTurnEnd` and a non-empty prompt action.

If `.kiro/hooks/` exists but is empty or contains only disabled hooks, treat as
"hooks configured but incomplete".

---

## gsd-2 Harness-Concept Mapping

When gsd-2 is detected as installed (Phase 1 step 10), the following gaps are
conditionally closed. List them under "Already in place" with the gsd-2
command that covers them:

| Gap | Closed by | Note in output |
|---|---|---|
| `init.sh` absent | `/gsd doctor` | "init.sh gap closed — `/gsd doctor` covers runtime health checks" |
| Judge audit (long-task exit criterion) | `/gsd verdict` | "Judge audit covered by `/gsd verdict pass\|needs-attention\|needs-remediation`" |

Do NOT silently omit these gaps. Always name the gsd-2 command that closes them.
